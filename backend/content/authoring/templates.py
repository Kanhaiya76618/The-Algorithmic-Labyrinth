"""Starter-code scaffolds served to the player, one per supported language.

Every question uses the same stdin -> stdout contract, so the scaffolds are
identical across questions. Language keys must match backend/judge/client.py.
"""

STARTER_CODE = {
    "python3": (
        "import sys\n"
        "\n"
        "def solve(data: str) -> str:\n"
        "    # data is the full stdin. Write your incantation here.\n"
        "    return \"\"\n"
        "\n"
        "print(solve(sys.stdin.read()))\n"
    ),
    "java": (
        "import java.util.*;\n"
        "\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        // Write your incantation here.\n"
        "    }\n"
        "}\n"
    ),
    "c++": (
        "#include <bits/stdc++.h>\n"
        "using namespace std;\n"
        "\n"
        "int main() {\n"
        "    ios_base::sync_with_stdio(false);\n"
        "    cin.tie(nullptr);\n"
        "    // Write your incantation here.\n"
        "    return 0;\n"
        "}\n"
    ),
    "c": (
        "#include <stdio.h>\n"
        "#include <stdlib.h>\n"
        "#include <string.h>\n"
        "\n"
        "int main(void) {\n"
        "    /* Write your incantation here. */\n"
        "    return 0;\n"
        "}\n"
    ),
}
