import subprocess
import re

from ..base import Base as BaseSource
from ...kind.base import Base as BaseKind

# TODO error handling
def _run_command(args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def _parse_output(output):
    return [_parse_line(line) for line in output.split('\n') if not re.match(r'^\s*$', line)]

def _parse_line(line):
    values = re.split(r'\s+', line, maxsplit=2)
    attached = values[0] == '(attached)'
    session_name = values[1]
    prefix = '* ' if attached else '  '
    return {
        'word': session_name,
        'abbr': prefix + session_name,
        'action__session': session_name
    }

class Source(BaseSource):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'tmux/session'
        self.kind = TmuxSession(vim)

    def gather_candidates(self, context):
        process = _run_command(['tmux', 'list-sessions', '-F', '#{?session_attached,(attached),} #{session_name}'])
        output = process.stdout.decode('utf-8')
        return _parse_output(output)

class TmuxSession(BaseKind):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'tmux/session'
        self.default_action = 'attach'

    def action_attach(self, context):
        [target] = context['targets']
        _run_command(['tmux', 'switch-client', '-t', target['action__session']])

