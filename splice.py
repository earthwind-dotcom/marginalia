import re
from pathlib import Path
p = Path("marginalia.html"); s = p.read_text(encoding="utf-8")
arts = Path("reflections_articles.html").read_text(encoding="utf-8").rstrip("\n")
toc  = Path("reflections_toc.html").read_text(encoding="utf-8").rstrip("\n")

end = s.index("<!-- ==================== ENCOUNTER")   # reflections view ends here
head, tail = s[:end], s[end:]

anchor_nav = "      </div>\n    </nav>"
i = head.rindex(anchor_nav)
head = head[:i] + toc + "\n" + head[i:]

anchor_main = "    </main>"
j = head.rindex(anchor_main)
head = head[:j] + arts + "\n" + head[j:]

p.write_text(head + tail, encoding="utf-8")
print("spliced")
