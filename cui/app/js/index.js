const ipc = require('electron').ipcRenderer;

class CommandsView {
    get $el() {
        return $('.ma-commands-view');
    }

    constructor() {

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
    }
};

ipc.on('test-one', (e, a) => { console.log('tesafwefwet'); });

$(function() {
    new WindowHandler();
});