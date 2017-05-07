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

    constructor() {
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

const ipc = require('electron').ipcRenderer;

ipc.on('test-one', (e, a) => { console.log('tesafwefwet'); });

$(function() {
    new WindowHandler();
});