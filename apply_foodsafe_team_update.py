from pathlib import Path
import shutil
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "templates" / "welcome.html"
TEAM = ROOT / "static" / "team"
required = ["amrutha.jpg", "aishwarya.jpg", "deekshitha.jpg", "inchara.jpg"]

if not TEMPLATE.exists():
    print("ERROR: templates/welcome.html not found. Copy this script beside manage.py.")
    sys.exit(1)

missing = [name for name in required if not (TEAM / name).exists()]
if missing:
    print("ERROR: Missing photo(s) in static/team/: " + ", ".join(missing))
    print("Copy the included static folder into your project root, merging folders if asked.")
    sys.exit(1)

html = TEMPLATE.read_text(encoding="utf-8")
if "<!-- FOODSAFE LEADERSHIP TEAM SECTION -->" in html:
    print("Leadership section already exists. No duplicate was added.")
    sys.exit(0)

marker = '<footer class="footer">'
if marker not in html:
    print('ERROR: Could not find <footer class="footer">. No changes made.')
    sys.exit(1)

section = r"""
<!-- FOODSAFE LEADERSHIP TEAM SECTION -->
<section class="team-section">
  <div class="team-heading">
    <div>
      <span class="team-eyebrow">THE PEOPLE BEHIND FOODSAFE</span>
      <h2>Meet Our Leadership Team</h2>
      <p>Working together to build trust, transparency and safer food supply chains.</p>
    </div>
    <div class="team-controls">
      <button type="button" class="team-scroll-btn" id="teamPrev" aria-label="Scroll team left">←</button>
      <button type="button" class="team-scroll-btn" id="teamNext" aria-label="Scroll team right">→</button>
    </div>
  </div>
  <div class="team-track" id="teamTrack" aria-label="FoodSafe leadership team">
    <article class="team-card">
      <div class="team-photo-wrap"><img src="{% static 'team/amrutha.jpg' %}" alt="Amrutha" class="team-photo" loading="lazy"></div>
      <div class="team-card-body"><span class="team-role">CEO</span><h3>Amrutha</h3><p>Vision, strategy and project leadership</p></div>
    </article>
    <article class="team-card">
      <div class="team-photo-wrap"><img src="{% static 'team/aishwarya.jpg' %}" alt="Aishwarya" class="team-photo" loading="lazy"></div>
      <div class="team-card-body"><span class="team-role">Co-Founder</span><h3>Aishwarya</h3><p>Product direction and team collaboration</p></div>
    </article>
    <article class="team-card">
      <div class="team-photo-wrap"><img src="{% static 'team/deekshitha.jpg' %}" alt="Deekshitha" class="team-photo" loading="lazy"></div>
      <div class="team-card-body"><span class="team-role">CTO</span><h3>Deekshitha</h3><p>Technology strategy and system architecture</p></div>
    </article>
    <article class="team-card">
      <div class="team-photo-wrap"><img src="{% static 'team/inchara.jpg' %}" alt="Inchara" class="team-photo" loading="lazy"></div>
      <div class="team-card-body"><span class="team-role">COO</span><h3>Inchara</h3><p>Operations and project coordination</p></div>
    </article>
  </div>
</section>
<style>
.team-section{margin-top:30px;padding:25px;background:#fff;border:1px solid var(--border);border-radius:16px;overflow:hidden}
.team-heading{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:20px}
.team-eyebrow{color:var(--green);font-size:10px;font-weight:800;letter-spacing:1.4px}
.team-heading h2{margin-top:8px;font-size:21px;letter-spacing:-.5px}
.team-heading p{margin-top:7px;color:var(--muted);font-size:12px;line-height:1.7}
.team-controls{display:flex;gap:8px;flex-shrink:0}
.team-scroll-btn{width:38px;height:38px;border:1px solid var(--border);border-radius:10px;background:#f7fbf8;color:var(--green);font-size:20px;cursor:pointer;transition:.2s}
.team-scroll-btn:hover{background:var(--green);color:#fff}
.team-track{display:grid;grid-auto-columns:minmax(220px,1fr);grid-auto-flow:column;gap:16px;overflow-x:auto;padding:2px 2px 12px;scroll-snap-type:x mandatory;scroll-behavior:smooth;scrollbar-width:thin;scrollbar-color:#b6d9c2 #f0f5f1}
.team-card{min-width:0;overflow:hidden;border:1px solid var(--border);border-radius:14px;background:#fff;scroll-snap-align:start;transition:transform .2s,box-shadow .2s}
.team-card:hover{transform:translateY(-3px);box-shadow:var(--shadow)}
.team-photo-wrap{height:235px;background:#edf4ef;overflow:hidden}
.team-photo{display:block;width:100%;height:100%;object-fit:cover;object-position:center 35%}
.team-card-body{padding:17px}
.team-role{display:inline-block;padding:6px 9px;background:var(--green-light);color:var(--green);border-radius:7px;font-size:10px;font-weight:800;letter-spacing:.5px}
.team-card-body h3{margin-top:12px;font-size:16px}
.team-card-body p{margin-top:7px;min-height:34px;color:var(--muted);font-size:11px;line-height:1.7}
@media(max-width:650px){.team-section{padding:16px}.team-heading{align-items:flex-start}.team-heading h2{font-size:18px}.team-heading p{max-width:270px}.team-track{grid-auto-columns:minmax(205px,78%)}.team-photo-wrap{height:220px}}
</style>
<script>
(function(){
 const track=document.getElementById("teamTrack"),prev=document.getElementById("teamPrev"),next=document.getElementById("teamNext");
 if(!track||!prev||!next)return;
 prev.addEventListener("click",()=>track.scrollBy({left:-track.clientWidth*.8,behavior:"smooth"}));
 next.addEventListener("click",()=>track.scrollBy({left:track.clientWidth*.8,behavior:"smooth"}));
})();
</script>
"""
backup = TEMPLATE.with_name("welcome.html.backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
shutil.copy2(TEMPLATE, backup)
TEMPLATE.write_text(html.replace(marker, section + "\n" + marker, 1), encoding="utf-8")
print("SUCCESS: Leadership section added.")
print("Backup created:", backup.name)
print("Now refresh the dashboard with Ctrl+F5.")
