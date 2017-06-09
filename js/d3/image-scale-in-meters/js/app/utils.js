export function str() {
    return "".concat.apply("",arguments);
}

export function startswith(str, substr) { 
    return str && str.indexOf(str) === 0;
};
