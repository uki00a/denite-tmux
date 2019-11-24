import subprocess
import re

from ..base import Base as BaseSource
from ...kind.base import Base as BaseKind
from denite.util import debug

# TODO error handling
# TODO refactor

def _run_command(args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

class Source(BaseSource):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'tmux/session'
        self.kind = TmuxSession(vim)

    def gather_candidates(self, context):
        process = _run_command(['tmux', 'list-sessions'])
        output = process.stdout.decode('utf-8')
        return self._parse_output(output)

    def _parse_output(self, output):
        return [self._parse_line(line) for line in output.split('\n') if not re.match(r"^\s$", line)]

    def _parse_line(self, line):
        values = re.split(r'\s+', line)
        session_name = values[0]
        return {
            'word': session_name,
            'abbr': session_name,
            'action__session': session_name
        }

class TmuxSession(BaseKind):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'tmux/session'
        self.default_action = 'attach'

    def action_attach(self, context):
        [target] = context['targets']
        _run_command(['tmux', 'switch-client', '-t', target['action__session']])

