# Autogenerated file
def render(info, scripts):
    yield """
<form name = 'frmselect' method = 'post'>
    <table cellpadding='4' border='1' frame='box' rules='all'>
       <TH width=\"30\">
       <TH>Name
       <TH>Status
       <TH>
       <TH>
        """
    for script in scripts:
        yield """
            """
        if script["name"] != '..' and script["name"] != '.':
            yield """ 
               <TR>
                    <TD><a class=\"button link\" href=\"/script_setting?id="""
            yield str(script["id"])
            yield """&oper=edit\">Edit</a>
                    <TD style=\"font-size: 12pt; font-weight: bold;\" >"""
            yield str(script["name"])
            yield """
                    <TD style=\"font-size: 12pt; font-weight: bold;\" ><span style=\"color:"""
            if script['enable'] == 'on':
                yield """Green"""
            else:
                yield """Red"""
            yield """\">"""
            yield str(script["enable"])
            yield """
                    <TD><a class=\"button link\" href=\"/script_setting?id="""
            yield str(script["id"])
            yield """&oper=del\">Del</a>
                    <TD><a class=\"button link\" href=\"/script_setting?id="""
            yield str(script["id"])
            yield """&oper=enable\">On/Off</a>
            """
        yield """
        """
    yield """            
       <TR>
          <TD colspan=\"3\"><a class=\"button link\" href=\"/script_setting?oper=add\">Add</a>
          <TD colspan=\"2\"><a class=\"button link\" href=\"/script_setting?oper=refresh\">Refresh</a>
   </table>
</form>
"""
