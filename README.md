# SMS Parse

Send a POST request to the `/parse_sms` endpoint to parse the SMS. Send a JSON body in this format -
```
{
    sms_text: "You've spent INR 1234.12 at 17:44 on June 20, 2023. If it wasn't done by you, ping us on the Fi app. -Federal Bank"
}
```

If you have an SMS that couldn't be parsed, please send me a sample at
my email: [mail@bibhasdn.com](mailto:mail@bibhasdn.com), or send a pull request.