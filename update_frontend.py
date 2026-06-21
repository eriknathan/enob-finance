import re

# 1. Update Cards in dashboard and month_detail
for filepath in ["templates/app_dashboard/dashboard.html", "templates/app_months/month_detail.html"]:
    with open(filepath, "r") as f:
        content = f.read()
    
    # Add hover classes to the stat cards
    content = content.replace(
        'shadow-sm p-5 transition-theme"', 
        'shadow-sm p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:border-gray-200 dark:hover:border-white/20"'
    )
    content = content.replace(
        'shadow-sm p-4 transition-theme"', 
        'shadow-sm p-4 transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:border-gray-200 dark:hover:border-white/20"'
    )

    # 2. Update Empty States
    # Find block: <div class="px-6 py-8 text-center">\n      <p class="text-sm text-[#454D60] dark:text-white/30">([^<]+)</p>\n    </div>
    def repl_empty_state(match):
        text = match.group(1)
        return f"""<div class="px-6 py-12 flex flex-col items-center justify-center text-center">
      <div class="w-12 h-12 rounded-full bg-gray-50 dark:bg-white/5 flex items-center justify-center mb-3">
        <svg class="w-6 h-6 text-gray-400 dark:text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
        </svg>
      </div>
      <p class="text-sm font-medium text-[#000918] dark:text-white/60 mb-1">Nada por aqui ainda</p>
      <p class="text-xs text-[#454D60] dark:text-white/30">{text}</p>
    </div>"""

    content = re.sub(r'<div class="px-6 py-8 text-center">\s*<p class="text-sm text-\[#454D60\] dark:text-white/30">([^<]+)</p>\s*</div>', repl_empty_state, content)
    
    with open(filepath, "w") as f:
        f.write(content)

# 3. Update topbar.html to add greeting
topbar_path = "templates/components/topbar.html"
with open(topbar_path, "r") as f:
    topbar = f.read()

greeting_html = """    <!-- Greeting -->
    <div class="hidden md:flex items-center gap-2 mr-2 border-r border-gray-200 dark:border-white/8 pr-4">
      <div class="flex flex-col items-end">
        <span class="text-[10px] uppercase tracking-widest text-[#454D60] dark:text-white/40">Olá,</span>
        <span class="text-sm font-semibold text-[#000918] dark:text-white">{{ user.email|truncatechars:25 }}</span>
      </div>
    </div>

    <!-- Logout -->"""

topbar = topbar.replace('<!-- Logout -->', greeting_html)

with open(topbar_path, "w") as f:
    f.write(topbar)

print("Updates applied successfully.")
