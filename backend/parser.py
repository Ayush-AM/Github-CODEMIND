import ast
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticNode:
    type: str
    name: str
    start_line: int
    end_line: int


class SemanticParser:
    DECLARATION_PATTERNS = [
        ("class", re.compile(r"^\s*(?:export\s+)?(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+([A-Za-z_]\w*)")),
        ("interface", re.compile(r"^\s*(?:export\s+)?(?:public\s+)?interface\s+([A-Za-z_]\w*)")),
        ("function", re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)\s*\(")),
        ("component", re.compile(r"^\s*(?:export\s+)?(?:const|let)\s+([A-Z][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?\(?")),
        ("function", re.compile(r"^\s*(?:export\s+)?(?:const|let)\s+([A-Za-z_]\w*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>")),
        ("method", re.compile(r"^\s*(?:public|private|protected|static|async|virtual|inline|\s)+\s*(?:[\w:<>,*&\[\]?]+\s+)+([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:const\s*)?\{")),
    ]

    def parse(self, content: str, language: str) -> list[SemanticNode]:
        if language == "python":
            return self._parse_python(content)
        if language in {"javascript", "typescript", "tsx", "jsx", "java", "cpp", "c", "header"}:
            return self._parse_brace_language(content)
        if language == "markdown":
            return self._parse_markdown(content)
        return []

    @staticmethod
    def _parse_python(content: str) -> list[SemanticNode]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        nodes: list[SemanticNode] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                node_type = "class" if isinstance(node, ast.ClassDef) else "function"
                nodes.append(SemanticNode(node_type, node.name, node.lineno, node.end_lineno or node.lineno))
        return sorted(nodes, key=lambda item: (item.start_line, -item.end_line))

    def _parse_brace_language(self, content: str) -> list[SemanticNode]:
        lines = content.splitlines()
        nodes: list[SemanticNode] = []
        for index, line in enumerate(lines):
            for node_type, pattern in self.DECLARATION_PATTERNS:
                match = pattern.match(line)
                if not match:
                    continue
                start = index + 1
                end = self._find_block_end(lines, index)
                nodes.append(SemanticNode(node_type, match.group(1), start, end))
                break
        return nodes

    @staticmethod
    def _find_block_end(lines: list[str], start_index: int) -> int:
        depth = 0
        opened = False
        for index in range(start_index, len(lines)):
            line = re.sub(r'(["\']).*?\1', '""', lines[index])
            for char in line:
                if char == "{":
                    depth += 1
                    opened = True
                elif char == "}":
                    depth -= 1
                    if opened and depth <= 0:
                        return index + 1
        return min(len(lines), start_index + 120)

    @staticmethod
    def _parse_markdown(content: str) -> list[SemanticNode]:
        headings: list[tuple[int, str]] = []
        for number, line in enumerate(content.splitlines(), 1):
            match = re.match(r"^#{1,6}\s+(.+)$", line)
            if match:
                headings.append((number, match.group(1).strip()))
        total = len(content.splitlines()) or 1
        return [
            SemanticNode("section", name, line, headings[index + 1][0] - 1 if index + 1 < len(headings) else total)
            for index, (line, name) in enumerate(headings)
        ]
