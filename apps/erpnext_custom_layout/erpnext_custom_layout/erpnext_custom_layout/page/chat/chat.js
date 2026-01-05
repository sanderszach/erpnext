frappe.pages['chat'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Chat',
		single_column: true,
		disable_sidebar_toggle: true,
	});

	const container = $('<div id="chat-ui-root" style="width: 100%; height: 100%; min-height: 500px;"></div>').appendTo(page.main);

	async function load_chat_ui() {
		try {
			// Define global share scope if not exists (minimal for MF)
			if (!window.__webpack_share_scopes__) {
				window.__webpack_share_scopes__ = { default: {} };
			}

			// Load the microfrontend
			const remoteUrl = 'http://localhost:3005/remoteEntry.js';
			const scope = 'chat_ui';
			const renderModule = './render';

			console.log('Loading chat UI from:', remoteUrl);

			if (!window[scope]) {
				const script = document.createElement('script');
				script.src = remoteUrl;
				script.async = true;
				script.crossOrigin = 'anonymous';
				
				await new Promise((resolve, reject) => {
					script.onload = resolve;
					script.onerror = reject;
					document.head.appendChild(script);
				});

				// Initialize the container - it needs to be told about its share scope
				// The MFE bundles its own React/ReactDOM, so we don't need to provide them
				if (window[scope].init) {
					await window[scope].init(window.__webpack_share_scopes__.default);
				}
			}

			// Get the render function from the MFE
			// This function handles all React/ReactDOM logic internally
			const renderFactory = await window[scope].get(renderModule);
			const renderModuleExports = renderFactory();
			const renderChat = renderModuleExports.default || renderModuleExports.renderChat || renderModuleExports;

			// Call the render function with the container element
			// This ensures we use the React/ReactDOM from the MFE bundle
			if (typeof renderChat === 'function') {
				renderChat(container[0]);
			} else {
				throw new Error('Render function not found in chat module');
			}

		} catch (error) {
			console.error('Failed to load Chat UI:', error);
			console.error('Error stack:', error.stack);
			container.html(`
				<div class="alert alert-danger" style="margin: 20px;">
					<h4>Failed to load Chat UI microfrontend</h4>
					<p>Make sure the chat-ui app is running on <code>http://localhost:3005</code></p>
					<pre>${error.message}</pre>
					<pre>${error.stack}</pre>
				</div>
			`);
		}
	}

	load_chat_ui();
}
