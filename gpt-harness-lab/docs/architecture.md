# Architecture

Le projet sépare volontairement les responsabilités afin que chaque pièce puisse
être remplacée indépendamment.

```text
CLI / application
       |
       v
    Harness ------> PromptLoader (.gpt)
       |  \
       |   +------> ConversationMemory
       |   +------> TraceWriter (.jsonl)
       |   +------> Evaluator
       v
    Provider <----> modèle mock ou OpenAI
       ^
       |
  ToolRegistry ---> calculator / current_time / text_stats
```

## Cycle d'une requête

1. Le harness compose les prompts `.gpt` configurés.
2. Il ajoute les derniers messages de la mémoire et la nouvelle demande.
3. Le fournisseur produit du texte ou une liste d'appels d'outils.
4. Le registre valide le nom de l'outil et exécute son gestionnaire.
5. Les résultats repartent vers le fournisseur jusqu'à la réponse finale.
6. La réponse est évaluée, mémorisée et enregistrée dans une trace JSONL.

La limite `max_tool_rounds` empêche une boucle infinie. Le calculateur n'utilise pas
`eval` : il accepte uniquement un petit sous-ensemble sûr de l'arbre syntaxique
Python. Le fournisseur `mock` est déterministe et garde les tests hors réseau.

## Frontières d'extension

- `Provider` définit le contrat d'un modèle.
- `ToolRegistry` expose des fonctions par schémas JSON.
- `PromptLoader` assemble les comportements depuis des fichiers texte.
- `evaluate_response` applique des contrôles rapides à chaque réponse.
- `ScenarioRunner` mesure des attentes reproductibles sur un jeu JSON.

