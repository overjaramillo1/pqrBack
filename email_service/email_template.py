BODY_HTML_template = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email Template</title>
<link rel="preconnect" href="
https://fonts.googleapis.com">
<link rel="preconnect" href="
https://fonts.gstatic.com"
crossorigin>
<link href="
https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;700&display=swap"
rel="stylesheet">
<style>
        body {
            font-family: 'Ubuntu', sans-serif;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
            text-align: start;
        }
        .header {
            color: #00aeef;
            font-weight: 600;
            font-size: 20px;
        }
        .dark {
            color: black;
            font-weight: 600;
            font-size: 20px;
        }
        a {
            color: #00aeef;
            font-weight: 600;
            font-size: 20px;
        }
        .message {
            color: #707070;
            font-size: 20px;
        }
        .footer {
            display:flex;
    flex-basis:1;
            color: black;
            font-weight: 600;
            font-size: 20px;
        }
</style>
</head>
<body>
<div class="container">
<div class="header">
            Hola $first_name, ¡buen día!
</div>
<hr>
<div class="message">
            $notification_message
</div>
<br>
<div class="footer">
<div >
        Confa. ¡Contigo, con todo!
</div >
<img src="
https://confa.co/ConfaImagenes/Recursos/vigilado_email.svg"
alt="logo" style="max-width: 100%; height: auto; margin-left: 200px">
</div>
<img src="
https://confa.co/ConfaImagenes/Recursos/logo_confa.svg"
alt="logo" style="max-width: 100%; height: auto;">
</div>
</body>
</html>
    """