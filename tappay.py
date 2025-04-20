import requests

# direct pay - pay by prime 
tappay_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
tappay_partner_key = "partner_g7KKkZEa7RlUs1SW3XpjMi48WFQSMhGMlQGb5fp8FPQxZOdrLRjPGzga"
tappay_merchant_id = "tppf_hshin0418_GP_POS_3"

def call_tappay(prime: str, amount: int, name: str, phone: str, email: str, order_number: str) -> dict:
    payload = {
        "prime": prime,
        "partner_key": tappay_partner_key,
        "merchant_id": tappay_merchant_id,
        "amount": amount,
        "order_number": order_number,
        "details": "訂單付款",
        "cardholder": {
            "phone_number": phone,
            "name": name,
            "email": email
        },
        "remember": False
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": tappay_partner_key
    }

    response = requests.post(tappay_URL, json=payload, headers=headers)
    return response.json()



