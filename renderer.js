async function ejecutarComandoFinanciero() {
    const userId = "usuario_actual";
    const comando = "transfiere 100 pesos a juan";
    
    const respuesta = await ipcRenderer.invoke(
        'financial-command', 
        {userId, command: comando}
    );
    
    console.log("Respuesta financiera:", respuesta);
}