// ==========================
// EFEITO DE DIGITAÇÃO
// ==========================

function escreverComAnimacao(texto){

let resultado = document.getElementById("resultado")

resultado.innerHTML = ""

let i = 0

function digitar(){

if(i < texto.length){

let char = texto[i]

if(char === "\n"){
resultado.innerHTML += "<br>"
}
else if(char === " "){
resultado.innerHTML += "&nbsp;"
}
else{
resultado.innerHTML += char
}

i++

setTimeout(digitar,20)

}

}

digitar()

}


// ==========================
// CONTINUAR HISTÓRIA
// ==========================

function continuar(){

let texto = document.getElementById("texto").value

fetch("/continuar",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
texto:texto
})
})
.then(res=>res.json())
.then(data=>{

escreverComAnimacao(data.response)

})

}


// ==========================
// REVISAR TEXTO
// ==========================

function revisar(){

let texto = document.getElementById("texto").value

fetch("/melhorar",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
texto:texto
})
})
.then(res=>res.json())
.then(data=>{

escreverComAnimacao(data.response)

})

}


// ==========================
// TRADUZIR TEXTO
// ==========================

function traduzir(){

let texto = document.getElementById("texto").value

fetch("/traduzir_literal",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
texto:texto
})
})
.then(res=>res.json())
.then(data=>{

escreverComAnimacao(data.response)

})

}


// ==========================
// GERAR IDEIA
// ==========================

function gerarIdeia(){

let tema = prompt("Tema da história:")

if(!tema){
return
}

fetch("/ideia",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
tema:tema
})
})
.then(res=>res.json())
.then(data=>{

escreverComAnimacao(data.response)

})

}


// ==========================
// CRIAR PERSONAGEM
// ==========================

function criarPersonagem(){

let descricao = prompt("Descrição do personagem:")

if(!descricao){
return
}

fetch("/personagem",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
descricao:descricao
})
})
.then(res=>res.json())
.then(data=>{

escreverComAnimacao(data.response)

})

}


// ==========================
// SALVAR HISTÓRIA
// ==========================

function salvarHistoria(){

let titulo = prompt("Título da história:")

if(!titulo){
return
}

let conteudo = document.getElementById("texto").value

fetch("/salvar_historia",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
titulo:titulo,
conteudo:conteudo
})
})
.then(res=>res.json())
.then(data=>{

alert(data.mensagem)

})

}


// ==========================
// SALVAR CAPÍTULO
// ==========================

function salvarCapitulo(){

let titulo = prompt("Título do capítulo:")

if(!titulo){
return
}

let historia_id = prompt("ID da história:")

if(!historia_id){
return
}

let conteudo = document.getElementById("texto").value

fetch("/salvar_capitulo",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
historia_id:historia_id,
titulo:titulo,
conteudo:conteudo
})
})
.then(res=>res.json())
.then(data=>{

alert(data.mensagem)

})

}


// ==========================
// LISTAR HISTÓRIAS
// ==========================

function listarHistorias(){

fetch("/listar_historias")
.then(res=>res.json())
.then(data=>{

let lista = document.getElementById("historiasList")

if(!lista){
return
}

lista.innerHTML = ""

data.historias.forEach(h=>{

let item = document.createElement("div")

item.innerHTML = "📖 " + h.titulo

item.onclick = function(){

listarCapitulos(h.id)

}

lista.appendChild(item)

})

})

}


// ==========================
// LISTAR CAPÍTULOS
// ==========================

function listarCapitulos(historia_id){

fetch("/listar_capitulos",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
historia_id:historia_id
})
})
.then(res=>res.json())
.then(data=>{

let lista = document.getElementById("capitulosList")

if(!lista){
return
}

lista.innerHTML = ""

data.capitulos.forEach(c=>{

let item = document.createElement("div")

item.innerHTML = "📄 " + c.titulo

item.onclick = function(){

carregarCapitulo(c.conteudo)

}

lista.appendChild(item)

})

})

}


// ==========================
// CARREGAR CAPÍTULO
// ==========================

function carregarCapitulo(conteudo){

document.getElementById("texto").value = conteudo

}
