"""
Generate Production Architecture Diagram for Atlassian Bug Dashboard
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(7, 9.5, 'Atlassian Cloud Migration Bug Intelligence Dashboard',
        fontsize=16, fontweight='bold', ha='center', va='center')
ax.text(7, 9.0, 'Production Architecture',
        fontsize=12, ha='center', va='center', color='gray')

# Define colors
github_color = '#24292e'
railway_color = '#0B0D0E'
vercel_color = '#000000'
postgres_color = '#336791'
fastapi_color = '#009688'
nextjs_color = '#000000'
cron_color = '#4CAF50'
jira_color = '#0052CC'
claude_color = '#D97757'
user_color = '#2196F3'

def draw_box(ax, x, y, width, height, color, label, sublabel=None):
    """Draw a rounded rectangle with label"""
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.02,rounding_size=0.1",
                         facecolor=color, edgecolor='white', linewidth=2, alpha=0.9)
    ax.add_patch(box)
    ax.text(x, y + (0.1 if sublabel else 0), label, fontsize=10, fontweight='bold',
            ha='center', va='center', color='white')
    if sublabel:
        ax.text(x, y - 0.25, sublabel, fontsize=8, ha='center', va='center', color='white', alpha=0.8)

def draw_arrow(ax, start, end, color='gray', style='-', label=None, curved=False):
    """Draw an arrow between two points"""
    if curved:
        arrow = FancyArrowPatch(start, end, arrowstyle='->', mutation_scale=15,
                                connectionstyle='arc3,rad=0.2',
                                color=color, linewidth=2, linestyle=style)
    else:
        arrow = FancyArrowPatch(start, end, arrowstyle='->', mutation_scale=15,
                                color=color, linewidth=2, linestyle=style)
    ax.add_patch(arrow)
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y + 0.2, label, fontsize=7, ha='center', va='center',
                color=color, style='italic')

# Draw components

# Users (top left)
draw_box(ax, 2, 7, 2, 0.8, user_color, 'Users', 'Browser')

# GitHub (top center)
draw_box(ax, 7, 7, 2, 0.8, github_color, 'GitHub', 'Source Control')

# Vercel (middle left)
draw_box(ax, 2, 4.5, 2.2, 1, vercel_color, 'Vercel', 'Next.js Frontend')

# Railway section (middle center-right)
# Railway container
railway_box = FancyBboxPatch((5, 2.8), 5.5, 3.2, boxstyle="round,pad=0.05,rounding_size=0.2",
                              facecolor='#1a1a2e', edgecolor='#4a4a6a', linewidth=2, alpha=0.3)
ax.add_patch(railway_box)
ax.text(7.75, 5.7, 'Railway', fontsize=11, fontweight='bold', ha='center', va='center', color='#888')

# FastAPI inside Railway
draw_box(ax, 6.5, 4.5, 2, 0.9, fastapi_color, 'FastAPI', 'Backend API')

# PostgreSQL inside Railway
draw_box(ax, 9, 4.5, 2, 0.9, postgres_color, 'PostgreSQL', 'Database')

# cron-job.org (bottom left)
draw_box(ax, 2, 2, 2.2, 0.8, cron_color, 'cron-job.org', 'Daily Scheduler')

# Atlassian Jira (bottom center)
draw_box(ax, 7, 1.5, 2.2, 0.8, jira_color, 'Atlassian Jira', 'Bug Source API')

# Claude Haiku (right side)
draw_box(ax, 12, 4.5, 2, 0.9, claude_color, 'Claude Haiku', 'AI Triage')

# Draw arrows/connections

# Users -> Vercel
draw_arrow(ax, (2, 6.6), (2, 5), user_color, label='HTTPS')

# GitHub -> Vercel (deploy)
draw_arrow(ax, (6, 7), (3.1, 7), github_color, label='Deploy')
ax.text(4.5, 7.3, 'git push', fontsize=7, ha='center', color='gray', style='italic')

# GitHub -> Railway (deploy)
draw_arrow(ax, (8, 7), (7.75, 6), github_color, label='Deploy')

# Vercel -> FastAPI
draw_arrow(ax, (3.1, 4.5), (5.5, 4.5), '#666', label='REST API')

# FastAPI <-> PostgreSQL
draw_arrow(ax, (7.5, 4.5), (8, 4.5), '#666')
draw_arrow(ax, (8, 4.3), (7.5, 4.3), '#666')
ax.text(7.75, 4.8, 'SQL', fontsize=7, ha='center', color='gray')

# cron-job.org -> FastAPI
draw_arrow(ax, (3.1, 2), (5.5, 4), cron_color, label='POST /sync')

# FastAPI -> Jira
draw_arrow(ax, (6.5, 4), (7, 2.3), jira_color, label='Fetch bugs')

# FastAPI -> Claude
draw_arrow(ax, (7.5, 4.5), (11, 4.5), claude_color, label='Triage request')

# Legend
legend_y = 0.5
ax.text(1, legend_y, 'Legend:', fontsize=9, fontweight='bold', va='center')

# Solid line
ax.plot([2.5, 3.5], [legend_y, legend_y], 'k-', linewidth=2)
ax.text(3.7, legend_y, 'Active connection', fontsize=8, va='center')

# Add flow numbers
ax.text(1.5, 6.1, '1', fontsize=12, fontweight='bold', color=user_color,
        bbox=dict(boxstyle='circle', facecolor='white', edgecolor=user_color))
ax.text(4.2, 6.7, '2', fontsize=12, fontweight='bold', color=github_color,
        bbox=dict(boxstyle='circle', facecolor='white', edgecolor=github_color))
ax.text(4.2, 4.8, '3', fontsize=12, fontweight='bold', color='#666',
        bbox=dict(boxstyle='circle', facecolor='white', edgecolor='#666'))
ax.text(3.5, 3.2, '4', fontsize=12, fontweight='bold', color=cron_color,
        bbox=dict(boxstyle='circle', facecolor='white', edgecolor=cron_color))
ax.text(6.2, 3, '5', fontsize=12, fontweight='bold', color=jira_color,
        bbox=dict(boxstyle='circle', facecolor='white', edgecolor=jira_color))
ax.text(9.5, 4.8, '6', fontsize=12, fontweight='bold', color=claude_color,
        bbox=dict(boxstyle='circle', facecolor='white', edgecolor=claude_color))

# Flow description
flow_text = """
Data Flow:
1. Users access dashboard via Vercel
2. Git push triggers deployment to Vercel & Railway
3. Frontend fetches data from FastAPI backend
4. cron-job.org triggers daily sync (POST /api/bugs/sync/incremental)
5. Backend fetches new/updated bugs from Atlassian Jira
6. Claude Haiku AI triages each bug (category, team, priority)
"""
ax.text(10.5, 1.5, flow_text, fontsize=8, va='top', ha='left',
        bbox=dict(boxstyle='round', facecolor='#f5f5f5', edgecolor='#ddd'),
        family='monospace')

plt.tight_layout()
plt.savefig('/home/user/atlassian-bug-dashboard/docs/architecture_diagram.pdf',
            format='pdf', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.savefig('/home/user/atlassian-bug-dashboard/docs/architecture_diagram.png',
            format='png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Architecture diagram saved to docs/architecture_diagram.pdf and docs/architecture_diagram.png")
