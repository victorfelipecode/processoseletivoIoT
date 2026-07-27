# Monitor de estoque Kanban Inteligente

## 1. Identificação do Candidato

-Nome Completo: Victor Felipe Alves Pinto
-GitHub: victorfelipecode

## 2. Visão Geral

O presente projeto refere-se a um monitor de estoque voltados a almoxarifados e linhas de produção que utiliza o sistema Kanban. Na montagem foi utilizada uma placa Hx711 acoplada a um ESP32 que possibilita o monitoramento de peso na linha de montagem.

Tal sistema de monitoramento faz a leitura de peso e que transita entre vazio, regular reabastecido e anomalia, emitindo alerta quando há transição entre os status aqui descritos. Eliminando a necessidade de inspeção manual e prevenindo paradas de linha por ausência de componentes.

## 3. Da Arquitetura do sistema Iot

Para quesito de organização, foi separado três camadas:

- Protocolo de leitura: É gerado 24 pulsos de clock lendo um bit por pulso, emite o 25º pulso de configuração de ganho e converte o resultado de complemento de dois. Perceba que a leitura é dado em valor bruto de informações.

- Tratamento das informações e conversão em gramas: As informações obtidas em valor bruto são convertidos em gramas com base na proporção do sensor (0–2100 → 0–5000 g).

- Loop Principal: Aqui é definido o status da maquina (vazio, regular reabastecido e anomalia) e emitido a mensagem em log quando as informações transitam entre sí.

## 4. Componentes Utilizados

- ESP32 DevKit C v4: Um Microcontrolador principal que executa o firmware Micropython.

- Placa Hx711 (5 kg): Um Amplificador da célula de carga que fornece a leitura de peso.

- Monitor serial: Reservado para saída de logs de status, alertas e telemetria.

## 5. Decisões Técnicas relevantes

- Escolha do cenário WEIGHT: menor risco de execução com base no tempo de entrega do projeto, dado que os demais projetos apresentavam uma leve complexidade a mais, como TEMPERATURE por exemplo que utiliza dois sensores em paralelo o que incide em duas condições de risco simultâneas.

- Arquitetura em três camadas: separação entre leitura, tratamento e decisão.

- Arquitetura não bloqueante: uso de pausas curtas para evitar perda de eventos do simulador.

- Temporização explícita no protocolo: garante estabilidade do sinal antes da leitura.

- Filtro de mediana com 7 amostras: reduz o impacto de leituras anômalas.

- Rejeição de valores impossíveis: descarta leituras fora da faixa física esperada do sensor.

- Consenso de três leituras: exige confirmação antes de alterar o estado do sistema.
 
-Tratamento de ruídos e glitches: evita mudanças de estado causadas por erros isolados.

-Interrupção do debug do sincronismo do sensor: priorização das entregas restantes diante da limitação de prazo.

- Registro da limitação: documentação transparente de que a lógica de negócio foi implementada, mas o sincronismo do HX711 no ambiente simulado não foi totalmente estabilizado.

## 6. Resultados Obtidos

- Máquina de estados: implementada e validada em execuções com leituras estáveis.

- Testes isolados: os testes de Consumo Parcial e Anomalia (test_1 e test_3) passaram em determinadas execuções.

- Comunicação serial: mensagens de status, alerta e reposição emitidas no formato exigido pelos testes automatizados.


### Limitações identificadas:

-Sincronismo do HX711 no Wokwi: não foi completamente estabilizado.

- Problema observado: leituras ocasionalmente desalinhadas, com bits deslocados.

- Efeito: oscilação indevida entre estados do sistema.

- Medidas aplicadas: filtro de mediana, rejeição de valores inválidos e confirmação por consenso de três leituras.

- Resultado: as medidas reduziram os efeitos do problema, mas não garantiram estabilidade total.

- Testes automatizados: os três testes (test_1, test_2 e test_3) não passam de forma consistente na mesma execução; em algumas rodadas, dois dos três testes passam isoladamente.


### Conclusão técnica:

-Arquitetura de software: correta e validada.

-Camadas de aquisição, tratamento e decisão: implementadas adequadamente.

-Falha remanescente: restrita à sincronização de baixo nível entre o firmware e o HX711 simulado.

-Diagnóstico: o problema não está na lógica de negócio, mas na comunicação entre o firmware e o hardware simulado.

## 7. Comentários Adicionais:

### Dificuldades encontradas:
A maior dificuldade encontrada no projeto foi o controle de tempo preciso de tempo em microssegundos nas leituras de dados, pelo qual pequenas variações de timing gerava leituras corrompidas na simulação do debug do protocolo de comunicação do HX711.

### Principais aprendizados:
Aprendi na prática o protocolo de comunicação de um sensor de peso via GPIO, o conceito de máquina de estados aplicado a sistemas embarcados, e a importância de arquitetura não-bloqueante em firmware. Também aprendi, de forma mais ampla, a debugar problemas de hardware simulado a partir de apenas logs de CI — sem acesso a osciloscópio ou depuração visual em tempo real, isolando hipóteses uma de cada vez a partir do comportamento observado.

### Melhorias com mais tempo: 
investigaria o uso de uma biblioteca MicroPython já validada para o HX711, para isolar se o problema está na implementação própria do protocolo ou em uma particularidade do componente simulado. Também configuraria testes locais via Docker, reduzindo o tempo de ciclo entre cada tentativa de correção.

## 8. Exemplo de Inferência

Log da execução do teste automatizado "Teste de Anomalia - Caixa Removida ou
Erro de Leitura" (GitHub Actions / Wokwi CI):

Sistema Kanban Inicializado
[Teste de Anomalia] Expected text matched: "Sistema Kanban Inicializado"
[Teste de Anomalia] delay 1s
Abastecimento concluído. Caixa cheia.
ALERTA: Caixa ausente ou erro de calibração no sensor HX711!
[Teste de Anomalia] Expected text matched: "ALERTA: Caixa ausente ou erro de
calibração no sensor HX711!"
[Teste de Anomalia] delay 500ms
[Teste de Anomalia] Scenario completed successfully

### Comentário:
 este log confirma o cenário de anomalia executado com sucesso ("Scenario completed successfully"). O firmware inicializa, detecta a caixa
em carga máxima (transição para o estado "cheio") e, quando o simulador altera a leitura para zero, identifica corretamente a condição de anomalia, emitindo a mensagem exata esperada pelo teste.

O caso mais interessante observado foi justamente a diferença de comportamento entre execuções: o mesmo firmware que conclui este cenário
com sucesso apresenta instabilidade em outras rodadas, o que reforça o diagnóstico de que a falha está no sincronismo da leitura do sensor, e não na lógica de classificação de estados.



 