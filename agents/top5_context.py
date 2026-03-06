# Naila — Génère un top 5 de contexte selon le département

def get_top5_context(department):

    contexts = {

        "IT Support": [
            "Users experiencing login issues should first reset their password.",
            "If password reset fails, the support team should verify account credentials.",
            "Users must confirm their registered email address.",
            "Account access issues may require investigation by IT support.",
            "Customers should be reassured while the issue is being resolved."
        ],

        "Billing and Payments": [
            "Billing issues may occur due to duplicate charges.",
            "Customers should verify the invoice number before requesting a refund.",
            "Refund requests must be reviewed by the billing team.",
            "Customers may need to provide transaction details.",
            "Billing issues should be handled promptly to maintain customer satisfaction."
        ],

        "Returns and Exchanges": [
            "Customers may request a return if the product received is incorrect.",
            "Products must generally be returned within the allowed return period.",
            "The support team should provide instructions for returning items.",
            "Customers may receive a replacement or refund depending on the case.",
            "Return requests should be processed quickly to ensure customer satisfaction."
        ],

        "Product Support": [
            "Customers may ask questions about product features or configuration.",
            "Support agents should explain product functionality clearly.",
            "Documentation may help customers understand product capabilities.",
            "Customers may request guidance on using specific features.",
            "Clear explanations help reduce customer confusion."
        ],

        "Customer Service": [
            "Customer service handles general customer concerns.",
            "Support agents should respond politely and professionally.",
            "Requests may involve account assistance or general inquiries.",
            "Customer satisfaction should remain a priority.",
            "Follow-up may be required to ensure the issue is resolved."
        ],

        "General Inquiry": [
            "Customers sometimes ask general questions about services.",
            "Support agents should respond clearly and helpfully.",
            "Additional information may be required to assist the customer.",
            "Requests may be redirected to the appropriate department.",
            "Maintaining a helpful tone is important."
        ]
    }

    return contexts.get(department, contexts["General Inquiry"])