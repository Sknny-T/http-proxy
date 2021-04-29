<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
    <link rel="stylesheet" href="sheet/stylesheet.css">
</head>
<body>

<ul>
  <li><a class="active" href="#">Lore</a></li>
  <li><a href="#">Ipsum</a></li>
  <li><a href="#">Dolor</a></li>
  <li><a href="#">Sit</a></li>
  <li class="image"><img src="img/logo.png"></li>
</ul>


<div class="login-page">
    <div class="form">
<form class="login-form" action="" method="post" name="Login_Form">
  <h2 id="login_head">Login</h2>
    <div class="input_field">
      <input name="Username" type="text" placeholder="Username">
        <span class="message">Credentials for debugging only: <br> Username: <b>"admin"</b> and Password: <b>"password"</b><br>Remove before deployment!</span>
    </div>
    <div class="input_field">
      <input name="Password" type="password" placeholder="Password">
    </div>
      <input name="Submit" type="submit" value="Login" class="button">

</form>
    </div>
</div>
</body>
</html>
