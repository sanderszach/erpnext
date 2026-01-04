frappe.pages['chat'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Chat'
	});

	const chat_html = `
		<div class="chat-container">
			<div class="chat-messages">
				<div class="message chat-placeholder">
					<em>Start a conversation with the ERP Agent...</em>
				</div>
			</div>
			<div class="input-group">
				<input type="text" class="form-control chat-input" placeholder="Type your message...">
				<button class="btn btn-primary send-btn" type="button">Send</button>
			</div>
		</div>
	`;
	$(chat_html).appendTo(page.main);

	const urlParams = new URLSearchParams(window.location.search);
	const query = urlParams.get('q');
	if (query) {
		page.main.find('.chat-input').val(query);
	}

	page.main.find('.send-btn').on('click', function() {
		const input = page.main.find('.chat-input');
		const message = input.val();
		if (message) {
			append_message('User', message);
			input.val('');
			// Simulate agent response
			setTimeout(() => {
				append_message('Agent', 'I received your message: ' + message);
			}, 1000);
		}
	});

	page.main.find('.chat-input').on('keypress', function(e) {
		if (e.which == 13) {
			page.main.find('.send-btn').click();
		}
	});

	function append_message(sender, text) {
		const msgHtml = `
			<div class="message">
				<strong>${sender}:</strong> <span>${text}</span>
			</div>
		`;
		page.main.find('.chat-messages').append(msgHtml);
		const container = page.main.find('.chat-messages');
		container.scrollTop(container[0].scrollHeight);
		
		// Remove placeholder on first message
		page.main.find('.chat-placeholder').remove();
	}
}
