# Mapa da ilha: servidor, transporte e persistência

```sh
python3 -B tools/validation/island_map_regression.py --loader fabric --eula-file /caminho/eula.txt
python3 -B tools/validation/island_map_regression.py --loader forge --eula-file /caminho/eula.txt
```

Requer JDK 21, dependências no cache e EULA já aceita fornecida pelo operador. O roteiro usa localhost, modo
offline e mundo descartável em `build/island-map-regression/`, com fontes arquivadas por revisão e compiladas
numa pasta temporária. Não usa os mundos do jogador nem servidores externos.

Ao contrário do perfil em mundo plano, este roteiro cria `terrassic:terrassic_small`, seed
`terrassic-map-regression`: continente real de raio 800, conforme o preset da revisão testada.
O levantamento assíncrono no servidor calcula o mapa; um cliente de protocolo recebe o pacote
`terrassic:island_map`. O jogador de teste fica em criativo para isolar o transporte de combate.

## Verificações

- Grade 128×128, extensão correspondente ao preset e dois vetores completos de altura/bioma.
- Categorias dentro do domínio 0..8, com mar e terra presentes.
- Arquivo `world/data/terrassic_island_map.dat` efetivamente criado após salvar e encerrar.
- Novo processo de servidor e nova conexão recebem os mesmos dados, comparados byte a byte.
- Cache preservado sem regravação: conteúdo e `mtime_ns` do arquivo continuam idênticos após o segundo encerramento.

O `results.json` registra a revisão, preset, raio, hashes dos dois vetores e resultado da execução. Logs e mundo
ficam no mesmo diretório. O primeiro teste chegou a receber o mapa, mas uma asserção imediata de mensagem do
logger correu antes da leitura de stdout e falhou (`fabric-8w62j9d1`); o log apareceu em seguida. Essa corrida do
observador foi eliminada. A validação usa pacote, arquivo e timestamp; não houve correção de produção por isso.

## Resultado em 25/10/2026

Revisão de runtime `f651ce99`, sem mudanças de produção na implementação do mapa durante esta validação:

| Loader | Diretório em `build/island-map-regression/` | Resultado |
|---|---|---|
| Fabric | `fabric-wryv_6ba` | Transporte, reinício e cache sem regravação passaram |
| Forge | `forge-ws0rc_v5` | Transporte, reinício e cache sem regravação passaram |

Os dois loaders produziram os mesmos dados para a seed/preset do roteiro: extensão 1.600, nível do mar 63,
nove categorias presentes. Hashes SHA-256 iguais nas execuções e após recarga:

- Alturas: `233c8632ba4dab83c6b6c00fddab0d54077e59c0ab1ae428cdbfa8346d0182be`
- Biomas: `04a1deb827a1585637c9ecb63f5c3123f8c32c7c45772b3004e679f1138885af`

## Limites da validação

O cliente não renderiza a imagem: cores, legenda, alinhamento, zoom, legibilidade e posição da seta continuam
precisando de teste no jogo. O roteiro não mede MSPT, não compara o levantamento com cada bloco da ilha e não
valida troca de dimensões ou parada do servidor durante um levantamento em andamento.
Na revisão visual, conferir também como seta e coordenadas são apresentadas no Nether e no End: o mapa recebido
descreve o continente do Overworld.
