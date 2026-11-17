// Copyright (c) 2025, Ecommerce contributors
// For license information, please see license.txt

// frappe.ui.form.on("Ecommerce Page", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("Ecommerce Page", {
    onload: function(frm) {
        // Hide the sidebar and the side section
        $(".form-sidebar, .layout-side-section").hide();

        render_preview(frm);
    },
    html_editor_test: function(frm) {
        render_preview(frm);
    }
});

function render_preview(frm) {
    const wrapper = frm.fields_dict.preview.$wrapper;

    wrapper.find("iframe").remove();

    const iframe = document.createElement("iframe");
    iframe.style.width = "100%";
    iframe.style.border = "0";
    wrapper[0].appendChild(iframe);

    const doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open();
    doc.write(`
        <html>
        <head>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="m-0 p-0 bg-gray-50">
            ${frm.doc.block_render || "<p class='text-gray-500'>No content</p>"}
        </body>
        </html>
    `);
    doc.close();

    function resizeIframe() {
        iframe.style.height = doc.body.scrollHeight + "px";
    }

    setTimeout(() => {
        resizeIframe();
        const buttons = doc.body.querySelectorAll("button");
        buttons.forEach(btn => {
            btn.addEventListener("click", () => {
                frappe.msgprint("Button clicked!");
            });
        });
    }, 50);
}
