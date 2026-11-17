import json
from pathlib import Path
import subprocess
import unittest

import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / "workflows" / "andy-issue-trigger.yml"

# Execute the exact inline GitHub Script with fake API calls and a persistent receipt list.
HARNESS = r"""
const fs = require('node:fs');
const { script, events, comments, labels, state } = JSON.parse(fs.readFileSync(0, 'utf8'));
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const record = new AsyncFunction('github', 'context', 'core', script);
const receipts = new Map(Object.entries(comments));
const calls = [];
const notices = [];
process.env.GITHUB_SERVER_URL = 'https://github.com';

const github = {
  rest: {
    issues: {
      async get({ issue_number }) {
        calls.push(issue_number);
        return { data: { state, labels: labels.map(name => ({ name })) } };
      },
      listComments() {},
      async createComment({ issue_number, body }) {
        const key = String(issue_number);
        const entries = receipts.get(key) || [];
        entries.push({ user: { id: 41898282, type: 'Bot' }, body });
        receipts.set(key, entries);
      }
    }
  },
  paginate: {
    async *iterator(method, { issue_number, per_page }) {
      if (method !== github.rest.issues.listComments || per_page !== 100) {
        throw new Error('Unexpected pagination request');
      }
      for (const comment of receipts.get(String(issue_number)) || []) {
        yield { data: [comment] };
      }
    }
  }
};

(async () => {
  // GitHub's concurrency group serializes jobs targeting the same issue.
  // This fake runner models that delivery and lets us verify the persisted result.
  for (const [index, payload] of events.entries()) {
    await record(github, {
      eventName: 'issues',
      payload,
      repo: { owner: 'jijanek', repo: 'Andy' },
      runId: index + 1
    }, { notice: message => notices.push(message) });
  }
  process.stdout.write(JSON.stringify({ calls, notices, receipts: Object.fromEntries(receipts) }));
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
"""


def event(label="andy-task", sender_id=323095460, sender_type="User", number=7):
    return {
        "action": "labeled",
        "repository": {"id": 1461109385},
        "issue": {
            "number": number,
            "user": {"id": 8},
            "body": "$(touch unsafe)\n</script>\n::warning::untrusted",
        },
        "label": {"name": label},
        "sender": {"id": sender_id, "type": sender_type},
    }


class IssueTriggerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # BaseLoader preserves the GitHub Actions key "on" under PyYAML.
        cls.workflow = yaml.load(WORKFLOW.read_text(), Loader=yaml.BaseLoader)
        cls.job = cls.workflow["jobs"]["diagnose"]
        cls.script = cls.job["steps"][0]["with"]["script"]

    def simulate(self, *events, comments=None, labels=("andy-task",), state="open"):
        run = subprocess.run(
            ["node", "-e", HARNESS],
            input=json.dumps({
                "script": self.script,
                "events": events,
                "comments": comments or {},
                "labels": labels,
                "state": state,
            }),
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
        return json.loads(run.stdout)

    def test_workflow_contract_and_permissions(self):
        self.assertEqual(self.workflow["on"], {"issues": {"types": ["labeled"]}})
        self.assertEqual(self.workflow["permissions"], {})
        self.assertEqual(self.job["permissions"], {"issues": "write"})
        self.assertEqual(self.job["runs-on"], "ubuntu-latest")
        self.assertEqual(len(self.job["steps"]), 1)
        step = self.job["steps"][0]
        self.assertRegex(step["uses"], r"^actions/github-script@[a-f0-9]{40}$")
        self.assertEqual(step["with"]["retries"], "0")
        self.assertNotIn("${{", self.script)
        for gate in (
            "github.repository_id == '1461109385'",
            "github.event.label.name == 'andy-task'",
            "github.event.sender.type == 'User'",
            "github.event.sender.id == 323095460",
            "github.actor_id == '323095460'",
            "github.triggering_actor == 'jijanek'",
        ):
            self.assertIn(gate, self.job["if"])

    def test_trusted_label_records_one_receipt_without_issue_content(self):
        result = self.simulate(event())
        self.assertEqual(result["calls"], [7])
        receipt, = result["receipts"]["7"]
        self.assertIn("actions/runs/1", receipt["body"])
        self.assertNotIn("untrusted", json.dumps(result))
        self.assertTrue(result["notices"][0].startswith("Accepted:"))

    def test_unrelated_label_makes_no_api_calls(self):
        result = self.simulate(event(label="bug"), event(label="ANDY-TASK"))
        self.assertEqual(result["calls"], [])
        self.assertEqual(result["receipts"], {})

    def test_untrusted_sender_or_bot_makes_no_api_calls(self):
        result = self.simulate(event(sender_id=101), event(sender_type="Bot"))
        self.assertEqual(result["calls"], [])
        self.assertEqual(result["receipts"], {})

    def test_removed_label_or_closed_issue_makes_no_write(self):
        for kwargs in ({"labels": ["bug"]}, {"state": "closed"}):
            with self.subTest(**kwargs):
                result = self.simulate(event(), **kwargs)
                self.assertEqual(result["calls"], [7])
                self.assertEqual(result["receipts"], {})

    def test_duplicate_on_later_page_is_skipped(self):
        forged = {"user": {"id": 8, "type": "User"}, "body": "<!-- andy:issue-trigger:diagnostic:v1 -->"}
        first = self.simulate(event(), comments={"7": [forged]})
        second = self.simulate(event(), comments=first["receipts"])
        self.assertEqual(len(second["receipts"]["7"]), 2)
        self.assertTrue(second["notices"][0].startswith("Duplicate:"))

    def test_concurrent_deliveries_queue_per_issue_and_deduplicate(self):
        self.assertEqual(self.job["concurrency"], {
            "group": "andy-issue-${{ github.event.issue.number }}",
            "cancel-in-progress": "false",
            "queue": "max",
        })
        result = self.simulate(event(), event(number=8), event())
        self.assertEqual({key: len(value) for key, value in result["receipts"].items()}, {
            "7": 1, "8": 1,
        })
        self.assertTrue(result["notices"][-1].startswith("Duplicate:"))


if __name__ == "__main__":
    unittest.main()
