frappe.pages['chat'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Chat'
	});

	const container = $('<div id="chat-ui-root" style="width: 100%; height: 100%; min-height: 500px;"></div>').appendTo(page.main);

	async function load_chat_ui() {
		try {
			// Load React and ReactDOM from CDN since we don't have them in the global scope easily
			if (!window.React) {
				await frappe.require('https://unpkg.com/react@18/umd/react.development.js');
				await frappe.require('https://unpkg.com/react-dom@18/umd/react-dom.development.js');
			}

			// Define global share scope if not exists (minimal for MF)
			if (!window.__webpack_share_scopes__) {
				window.__webpack_share_scopes__ = { default: {} };
			}

			// Load the microfrontend
			const remoteUrl = 'http://localhost:3001/remoteEntry.js';
			const scope = 'chat_ui';
			const module = './Chat';

			if (!window[scope]) {
				const script = document.createElement('script');
				script.src = remoteUrl;
				script.async = true;
				
				await new Promise((resolve, reject) => {
					script.onload = resolve;
					script.onerror = reject;
					document.head.appendChild(script);
				});

				// Initialize the container - it needs to be told about its share scope
				// In a non-webpack host, we might need a shim or just skip if shared are provided via globals
				if (window[scope].init) {
					await window[scope].init(window.__webpack_share_scopes__.default);
				}
			}

			const factory = await window[scope].get(module);
			const ChatComponent = factory().default;

			const root = ReactDOM.createRoot(container[0]);
			root.render(React.createElement(ChatComponent));

		} catch (error) {
			console.error('Failed to load Chat UI:', error);
			container.html(`
				<div class="alert alert-danger" style="margin: 20px;">
					<h4>Failed to load Chat UI microfrontend</h4>
					<p>Make sure the chat-ui app is running on <code>http://localhost:3001</code></p>
					<pre>${error.message}</pre>
				</div>
			`);
		}
	}

	load_chat_ui();
}
