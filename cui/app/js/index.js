const ipc = require('electron').ipcRenderer;

class CommandsView {
    get $el() {
        return $('.ma-commands-view');
    }

    constructor() {

    }

    appendResult(error, result, extra) {
        let data = JSON.parse(extra);

        let $resultElement = $('<div>', {'class': 'ma-command-container'});

        let $headerElement = $('<div>', {'class': 'ma-command-header'});
        
        let $preElement = $('<pre>', {'class': 'ma-command-result'});

        $headerElement.text('[' + data['index'] + '] >> ' + data['command']);

        $preElement.text(data["result"]);

        this.$el.append($resultElement.append($headerElement, $preElement));

        this.$el.animate({
            scrollTop: this.$el.find('.ma-command-container:last').offset().top
        }, 100);
        this.$el.animate({
            scrollTop: this.$el.find('.ma-command-container:last').offset().top
        }, 100);
    }
}

class CommandEditor {
    get $el() {
        return $('.ma-command-enter');
    }

    get $input() {
        return $('.ma-command-input');
    }

    constructor() {
        this.bind();
    }

    bind() {
        this.$input.on('keyup', (e) => {
            if (e.keyCode == 13) {
                ipc.send('send-command', this.$input.val(), 0);
            }
        });
    }
}

class CommandsPane {
    constructor() {
        this.commandsView = new CommandsView();
        this.commandEditor = new CommandEditor();

        this.bind();
    }

    bind() {
        ipc.on('command-result', $.proxy(this.commandReturn, this));
    }

    resize() {
        this.commandsView.$el.css('height', (window.innerHeight-60)+'px');
    }

    commandReturn(error, result, extra) {
        this.commandsView.appendResult(error, result, extra);
    }
};

class WindowHandler {
    constructor() {
        this.commandsPane = new CommandsPane();
  
        this.bind();
        this.resize();
    }

    bind() {
        $(window).on('resize', $.proxy(this.resize, this));
    }

    resize(e) {
        this.commandsPane.resize();
    }
};

$(function() {
    new WindowHandler();
});