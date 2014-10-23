# disqus.coffee: Handle the reply of disqus plugin.

casper = require('casper').create
    clientScripts: ['jquery.min.js']
    logLevel: 'info'
    verbose: true

# Remove default options passed by the Python executable
casper.cli.drop "cli"
casper.cli.drop "casper-path"

post_url = casper.cli.get(0)
content = casper.cli.get('content')
timeout = 10*1000

# casper.page.switchToChildFrame doesn't make sense. When I pass 5 to it, the
# page isn't switching to the sixth iframe as I expected. Maybe this function
# doesn't take literal order index as parameter. So I decide to switch to each 
# iframe until the title is what I want.
casper.switchToChildFrameByTitle = (title) -> 
    frames = @getElementsInfo 'iframe'
    for i in [0...frames.length]
        @page.switchToChildFrame(i)
        if @getTitle() is title
            return
        else
            @page.switchToParentFrame()

casper.start post_url

casper.waitForSelector '#disqus_thread', ->
    @switchToChildFrameByTitle 'Disqus 评论'
, ->
    @echo 'Reply Error'
    @exit(-1)
, timeout

casper.waitForSelector 'div#form', ->
    @evaluate (content) ->
        $('div.textarea').html "<p>#{content}</p>"
        $('input[name="author-guest"]').attr 'checked', true
        $('input[name="display_name"]').val 'Guest'
        $('input[name="email"]').val 'Guest@gmail.com'
        $('form').submit()
    , content
, ->
    @echo 'Reply Error'
    @exit(-1)
, timeout 
    
casper.waitForText content, ->
    @echo 'Reply OK'
, ->
    @echo 'Reply Error'
    @exit(-1)
, timeout 

casper.run()

