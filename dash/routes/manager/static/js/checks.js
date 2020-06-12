function validate_username(user){
    let isClean  = /[^A-Za-z0-9)(*&^$!`\_+={};:@~#>.<]/
    return isClean.test(user)
}

function check_username() {
    const form = document.forms['login'] || document.forms['verify']
	if (validate_username(form['username'].value)) {
        username.setCustomValidity("Your username is not suitable as it includes special characters.")
        return false
    }
    else if(form['username'].value.length < 4 || form['username'].value.length > 12){
        username.setCustomValidity("Your username is not suitable, it has to be between 4-12 characters.")
        return false
    }
    else{
        username.setCustomValidity('')
        return true
    }
}

function check_password() {
    const form = document.forms['profile']
	if (form['password'].value.length < 5) {
        password.setCustomValidity("Your password has to be longer than 5 characters!");
        return false;
    }
    else{
        password.setCustomValidity('');
    }
}

function match_password(){
    const form = document.forms['profile']
    if (form['password'].value !== form['password_confirm'].value){
        password_confirm.setCustomValidity("Make sure you entered the same password as before!");
    }
    else{
        password_confirm.setCustomValidity('');
    }
}

function match_email(){
    const form = document.forms['profile']
    if (form['email'].value !== form['email_confirm'].value){
        email_confirm.setCustomValidity("Make sure you entered the same email as before!");
    }
    else{
        email_confirm.setCustomValidity('');
    }
}
