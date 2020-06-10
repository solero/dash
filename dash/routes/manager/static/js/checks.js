function validate_username(user){
    let isClean  = /[^A-Za-z0-9)(*&^$!`\_+={};:@~#>.<]/
    return isClean.test(user)
}

function check_username() {
    const form = document.forms['login']
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