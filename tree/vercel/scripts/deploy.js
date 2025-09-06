async function main() {
  // Obtenemos la dirección que está desplegando el contrato
  const [deployer] = await ethers.getSigners();

  console.log("Desplegando contratos con la cuenta:", deployer.address);

  // Obtenemos el artefacto del contrato que queremos desplegar
  const Token = await ethers.getContractFactory("AEIO_MR_TOKEN");

  // Desplegamos el contrato, pasando la dirección del desplegador como el propietario inicial
  const token = await Token.deploy(deployer.address);

  // Esperamos a que el contrato sea desplegado
  await token.waitForDeployment();

  // Imprimimos la dirección del contrato desplegado
  console.log("Token AEIO-MR desplegado en:", await token.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
