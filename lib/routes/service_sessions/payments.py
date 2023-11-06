# import stripe
#
#
# stripe.api_key = "sk_test_51O2alEFxYpxLheef0ZI9Vo0a4FVY1iDuTMRmooyQzS9X2h2B9GkjyRL31RRYQoOM5ItSv0cqLyrIxdlvsDd8IRM3004cnfmqXI"
#
# 1
# invoice = stripe.PaymentIntent.create(
#   amount=2000,
#   currency="gbp",
#   automatic_payment_methods={"enabled": True},
# )
#
# print(invoice)

# url = "https://api.stripe.com/v1/payment_intents"
# key = "pk_test_51O2alEFxYpxLheef7f9RjVCkfju7aTEzjsdDyEvyIZ3ZqCIJrFjZB182NRoMOAxsDFSxQDRWZkSEifrL1klPZWVa00P9W72lzd"
# params = {
#
#     "amount": 2000,
#     "currency": "gbp",
#     "automatic_payment_methods[enabled]": True
# }
#
# headers = {
#     "sk_test_your_key": key
# }
#
# res = requests.get(f'{url}', params=params,)
#
# print(res.status_code)
# print(res.json())
