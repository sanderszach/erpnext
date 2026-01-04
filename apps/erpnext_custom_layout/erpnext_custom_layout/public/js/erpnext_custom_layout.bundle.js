frappe.provide('frappe.ui');

frappe.ui.NexERPSidebar = class {
    constructor() {
        console.log("NexERPSidebar: Initializing...");
        this.setup();
    }

    setup() {
        this.make_dom();
        this.render();
        this.bind_events();
        this.setup_breadcrumbs();
        this.move_sidebar_toggle();
    }

    move_sidebar_toggle() {
        const $toggle = $('.sidebar-toggle-btn');
        const $page_actions = $('.page-actions');
        if ($toggle.length && $page_actions.length && !$toggle.parent().hasClass('page-actions')) {
            $toggle.appendTo($page_actions);
        }
    }

    setup_breadcrumbs() {
        if (frappe.breadcrumbs && !frappe.breadcrumbs._custom_overridden) {
            const me = this;
            const old_clear = frappe.breadcrumbs.clear;
            
            frappe.breadcrumbs.clear = function() {
                const $page_head = $('.page-head:visible');
                if ($page_head.length) {
                    let $custom = $page_head.find('.custom-breadcrumbs');
                    if (!$custom.length) {
                        const $wrapper = $('<div class="custom-breadcrumbs-wrapper"><div class="container"><ul class="custom-breadcrumbs"></ul></div></div>').prependTo($page_head);
                        $custom = $wrapper.find('.custom-breadcrumbs');
                    }
                    this.$breadcrumbs = $custom.empty();
                } else {
                    old_clear.apply(this, arguments);
                }
            };
            frappe.breadcrumbs._custom_overridden = true;
        }
        
        // Initial update
        if (frappe.breadcrumbs) {
            frappe.breadcrumbs.update();
        }
    }

    make_dom() {
        this.$sidebar = $('.body-sidebar, .layout-side-section').first();
        if (!this.$sidebar.length) return;

        this.$sidebar.find('.nexerp-sidebar-wrapper').remove();
        this.$wrapper = $('<div class="nexerp-sidebar-wrapper">').appendTo(this.$sidebar);

        if (!$('.nexerp-modal-overlay').length) {
            this.make_modules_modal();
        }

        this.update_header();
    }

    update_header() {
        const $header = $('.sidebar-header');
        if ($header.length) {
            $header.off('click'); // Disable Frappe's default dropdown toggle
            $header.html(`
                <a href="/desk/home" class="nexerp-header-link">
                    <span class="lighting-logo">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                        </svg>
                    </span>
                    <span class="erp-text">ERP</span>
                </a>
            `);

            // Prevent any parent click handlers from triggering the dropdown
            $header.find('.nexerp-header-link').on('click', (e) => {
                e.stopPropagation();
            });
        }
    }

    get_current_workspace() {
        const route = frappe.get_route();
        if (route[0] === 'Workspaces' && route[1]) {
            return route[1];
        }
        return frappe.app.sidebar ? frappe.app.sidebar.workspace_title : 'Home';
    }

    get_sidebar_items() {
        const workspace = this.get_current_workspace();
        if (!workspace) return [];

        const sidebar_data = frappe.boot.workspace_sidebar_item[workspace.toLowerCase()];
        console.log('my sidebar data',sidebar_data);
        return sidebar_data ? sidebar_data.items : [];
    }

    slugify(text) {
        if (!text) return "";
        return text.toString().toLowerCase()
            .replace(/\s+/g, '-')           // Replace spaces with -
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\-\-+/g, '-')         // Replace multiple - with single -
            .replace(/^-+/, '')             // Trim - from start of text
            .replace(/-+$/, '');            // Trim - from end of text
    }

    make_modules_modal() {
        const modules = [
            { label: "Payables", route: "payables", icon: "arrow-left" },
            { label: "Receivables", route: "receivables", icon: "arrow-right" },
            { label: "Accounting", route: "accounting", icon: "bill" },
            { label: "Opening & Closing", route: "opening-closing", icon: "list" },
            { label: "Taxes", route: "taxes", icon: "list" },
            { label: "Budget", route: "budget", icon: "bill" },
            { label: "Banking", route: "banking", icon: "list" },
            { label: "Subscription", route: "subscription", icon: "bill" },
            { label: "Reports", route: "financial-reports", icon: "file-text" },
            { label: "Buying", route: "buying", icon: "shopping-cart" },
            { label: "Selling", route: "selling", icon: "tag" },
            { label: "Stock", route: "stock", icon: "package" },
            { label: "Assets", route: "assets", icon: "box" },
            { label: "Projects", route: "projects", icon: "briefcase" },
            { label: "CRM", route: "crm", icon: "users" },
            { label: "Support", route: "support", icon: "life-buoy" },
            { label: "Manufacturing", route: "manufacturing", icon: "settings" },
            { label: "Quality", route: "quality", icon: "check-circle" },
            { label: "Website", route: "website", icon: "globe" },
            { label: "Integrations", route: "integrations", icon: "layers" },
            { label: "Users", route: "users", icon: "user" },
            { label: "Settings", route: "settings", icon: "sliders" },
            { label: "Home", route: "home", icon: "home" }
        ];

        // Sort modules alphabetically by label
        modules.sort((a, b) => a.label.localeCompare(b.label));

        const grid_items_html = modules.map(m => `
            <div class="module-grid-item" data-route="/desk/${this.slugify(m.route)}/">
                <div class="module-icon-wrapper">
                    ${frappe.utils.icon(m.icon, "sm")}
                </div>
                <div class="module-label">${m.label}</div>
            </div>
        `).join('');

        const modal_html = `
            <div class="nexerp-modal-overlay">
                <div class="nexerp-modules-modal">
                    <div class="modal-close">
                        ${frappe.utils.icon("close", "xs")}
                    </div>
                    <div class="modules-grid">
                        ${grid_items_html}
                    </div>
                </div>
            </div>
        `;

        $('body').append(modal_html);

        $('.nexerp-modal-overlay, .modal-close').on('click', (e) => {
            if (e.target === e.currentTarget || $(e.currentTarget).hasClass('modal-close')) {
                $('.nexerp-modal-overlay').removeClass('show');
            }
        });

        $('.module-grid-item').on('click', (e) => {
            const url = $(e.currentTarget).data('route');
            if (url) {
                window.location.href = url;
                $('.nexerp-modal-overlay').removeClass('show');
            }
        });
    }

    render() {
        if (!this.$wrapper) return;

        this.update_header();

        const workspace = this.get_current_workspace();
        const items = this.get_sidebar_items();

        const context_items_html = items
            .filter(item => item.type !== 'Section Break' && item.hidden !== 1)
            .map(item => {
                const has_children = item.child_items && item.child_items.length > 0;
            const target_url = `/desk/${this.slugify(item.link_to || item.label)}`;
            
            return `
                <div class="nexerp-menu-item context-item" data-url="${target_url}">
                    <div class="item-left">
                        <span class="item-icon">${frappe.utils.icon(item.icon || 'file-text', 'sm')}</span>
                        <span class="item-label">${item.label}</span>
                    </div>
                    ${has_children ? `
                        <div class="chevron">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 18l6-6-6-6"></path>
                            </svg>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');

        this.$wrapper.html(`
            <div class="nexerp-sidebar-section">
                <div class="nexerp-menu-item" id="modules-toggle">
                    <div class="item-left">
                        <span class="item-icon">${frappe.utils.icon('grid', 'sm')}</span>
                        <span class="item-label">MODULES</span>
                    </div>
                    <div class="chevron">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 18l6-6-6-6"></path>
                        </svg>
                    </div>
                </div>
            </div>

            <div class="nexerp-sidebar-section">
                <div class="section-title">FAVORITES</div>
                <div class="nexerp-favorites-list">
                    <div class="nexerp-menu-item">
                        <div class="item-left">
                            <span class="star-icon">★</span>
                            Sales Dashboard
                        </div>
                    </div>
                    <div class="nexerp-menu-item">
                        <div class="item-left">
                            <span class="star-icon">★</span>
                            Monthly P&L
                        </div>
                    </div>
                </div>
            </div>

            <div class="nexerp-sidebar-section nexerp-context-section">
                <div class="section-title">${workspace.toUpperCase()}</div>
                <div class="context-items-list">
                    ${context_items_html}
                </div>
            </div>

            <div class="nexerp-sidebar-section recent-section" style="margin-top: auto;">
                <div class="section-title">RECENT</div>
                <div class="nexerp-recent-card">
                    <div class="card-title">Stock Update #9920</div>
                    <div class="card-meta">2 mins ago</div>
                </div>
                <div class="nexerp-recent-simple">Q3 Projection Draft</div>
            </div>
        `);
    }

    bind_events() {
        $('#modules-toggle').on('click', () => {
            $('.nexerp-modal-overlay').addClass('show');
        });

        this.$wrapper.on('click', '.context-item', (e) => {
            const url = $(e.currentTarget).data('url');
            if (url) {
                window.location.href = url;
            }
        });
    }
};

function init_nexerp_sidebar() {
    const sidebar = new frappe.ui.NexERPSidebar();
    sidebar.move_sidebar_toggle();
    
    // Update Search Bar Placeholder
    const search_input = $('#navbar-search');
    if (search_input.length) {
        search_input.attr('placeholder', __('Search or Chat'));
    }
}

$(document).ready(() => {
    setTimeout(init_nexerp_sidebar, 1000);
});

$(document).on('app_ready page-change', function() {
    setTimeout(init_nexerp_sidebar, 100);
});

if (frappe.ui.Sidebar) {
    const old_make_sidebar = frappe.ui.Sidebar.prototype.make_sidebar;
    frappe.ui.Sidebar.prototype.make_sidebar = function() {
        old_make_sidebar.apply(this, arguments);
        init_nexerp_sidebar();
    };
}

const observer = new MutationObserver((mutations) => {
    for (let mutation of mutations) {
        if (mutation.addedNodes.length && $('.body-sidebar').length && !$('.nexerp-sidebar-wrapper').length) {
            init_nexerp_sidebar();
        }
    }
});

observer.observe(document.body, { childList: true, subtree: true });

// Override AwesomeBar to change "Search for" to "Begin chat"
if (frappe.search && frappe.search.AwesomeBar) {
    frappe.search.AwesomeBar.prototype.make_global_search = function(txt) {
        if (txt.charAt(0) === "#") {
            return;
        }

        this.options.push({
            label: `
                <span class="flex justify-between text-medium">
                    <span class="ellipsis">${__("Begin chat {0}", [frappe.utils.xss_sanitise(txt).bold()])}</span>
                    <kbd>↵</kbd>
                </span>
            `,
            value: __("Begin chat {0}", [frappe.utils.xss_sanitise(txt)]),
            match: txt,
            index: 100,
            default: "Search",
            onclick: function () {
                frappe.ui.make_chat_dialog(txt);
            },
        });
    };
}

// Chat Dialog Implementation
frappe.ui.make_chat_dialog = function(initial_message) {
    const dialog = new frappe.ui.Dialog({
        title: __('Chat with ERP Agent'),
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'chat_html'
            }
        ],
    });

    dialog.fields_dict.chat_html.$wrapper.html(`
        <div class="chat-container" style="height: 400px; display: flex; flex-direction: column;">
            <div class="chat-messages" style="flex: 1; overflow-y: auto; padding: 15px; border: 1px solid var(--nexerp-border); border-radius: 8px; margin-bottom: 15px; background: var(--nexerp-bg);">
                <div class="message chat-placeholder" style="color: var(--nexerp-text-muted); text-align: center; margin-top: 150px;">
                    <em>Start a conversation with the ERP Agent...</em>
                </div>
            </div>
            <div class="input-group" style="display: flex; gap: 10px;">
                <input type="text" class="form-control chat-input" placeholder="Type your message..." style="background: var(--nexerp-hover); border: 1px solid var(--nexerp-border); color: var(--nexerp-text-primary);">
                <button class="btn btn-primary send-btn" type="button" style="background: var(--nexerp-accent-blue); border: none;">Send</button>
            </div>
        </div>
    `);

    const $messages = dialog.fields_dict.chat_html.$wrapper.find('.chat-messages');
    const $input = dialog.fields_dict.chat_html.$wrapper.find('.chat-input');
    const $send_btn = dialog.fields_dict.chat_html.$wrapper.find('.send-btn');

    function append_message(sender, text) {
        const is_user = sender === 'User';
        const msgHtml = `
            <div class="message" style="margin-bottom: 15px; display: flex; flex-direction: column; align-items: ${is_user ? 'flex-end' : 'flex-start'};">
                <div style="font-weight: 700; font-size: 10px; margin-bottom: 4px; color: var(--nexerp-text-muted); text-transform: uppercase; letter-spacing: 0.5px;">${__(sender)}</div>
                <div style="font-size: 14px; padding: 10px 14px; border-radius: 12px; max-width: 85%; background: ${is_user ? 'var(--nexerp-accent-blue)' : 'var(--nexerp-hover)'}; color: #fff; border: 1px solid var(--nexerp-border);">
                    ${text}
                </div>
            </div>
        `;
        $messages.append(msgHtml);
        $messages.scrollTop($messages[0].scrollHeight);
        $messages.find('.chat-placeholder').remove();
    }

    function handle_send() {
        const message = $input.val();
        if (message) {
            append_message('User', message);
            $input.val('');
            
            // Simulate agent response
            setTimeout(() => {
                append_message('Agent', 'I received your message: ' + message);
            }, 1000);
        }
    }

    $send_btn.on('click', handle_send);
    $input.on('keypress', function(e) {
        if (e.which == 13) {
            handle_send();
        }
    });

    dialog.show();

    if (initial_message) {
        append_message('User', initial_message);
        // Simulate agent response for initial message
        setTimeout(() => {
            append_message('Agent', 'I received your message: ' + initial_message);
        }, 1000);
    }
};
