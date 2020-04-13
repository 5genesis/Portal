function configureButton(input, trigger, ret)
{
    var fileInput = document.querySelector( input ),
        button = document.querySelector( trigger ),
        the_return = document.querySelector( ret);

    if (fileInput == null || button == null || the_return == null){ return; }

    button.addEventListener( "click", function(event) {
        fileInput.focus();
        return false;
    });

    fileInput.addEventListener("change", function( event ) {
        the_return.innerHTML = this.value.split("\\")[2];
    });
}

document.querySelector("html").classList.add('js');

configureButton(".input-fileVnfd", ".input-file-triggerVnfd", ".file-returnVnfd");
configureButton(".input-fileVim", ".input-file-triggerVim", ".file-returnVim");
configureButton(".input-fileNsd", ".input-file-triggerNsd", ".file-returnNsd");
