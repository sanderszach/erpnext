app_name = "erpnext_custom_layout"
app_title = "ERPNext Custom Layout"
app_publisher = "Zachary Sanders"
app_description = "Custom layout for ERPNext"
app_email = "zach@example.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "erpnext_custom_layout.bundle.css"
app_include_js = "erpnext_custom_layout.bundle.js"

website_route_rules = [
    {"from_route": "/desk/chat", "to_route": "chat"},
]
