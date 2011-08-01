%from bottle import url
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <title>Chat Demo</title>
    <link rel="stylesheet" href="{{ url("static", filename='chat.css') }}" type="text/css"/>
  </head>
  <body>
  <h3>Webchat using <a href="http://bottlepy.org">Bottle</a> with gevent server adapter to example async calls</h3>

  <div id="nav">
      <a href="http://bitbucket.org/iurisilvio/gevent/src/default/examples/webchat/">Source Code</a><br>
      Based on <a href="https://bitbucket.org/denis/gevent/src/tip/examples/webchat">gevent webchat example</a>
    </div>
    <div id="body">
      <div id="inbox">
  %for message in messages:
      %include message.tpl message=message
	%end
      </div>
      <div id="input">
	<form action="/a/message/new" method="post" id="messageform">
	  <table>
	    <tr>
          <td><input type="text" name="body" id="message" style="width:500px"/></td>
	      <td style="padding-left:5px">
		<input type="submit" value="Post"/>
	      </td>
	    </tr>
	  </table>
	</form>
      </div>
    </div>
    <script src="{{ url("static", filename='jquery-1.6.2.min.js') }}" type="text/javascript"></script>
    <script src="{{ url("static", filename='chat.js') }}" type="text/javascript"></script>
  </body>
</html>
