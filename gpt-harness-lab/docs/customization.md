# Personnalisation

## Ajouter un prompt

Créez `prompts/mon_role.gpt`, puis ajoutez `"mon_role"` à `prompt_files` dans la
configuration. Les variables `{{nom}}` peuvent être fournies à `PromptLoader.render`.

## Ajouter un outil

Déclarez un `Tool` dans `gpt_harness/tools/builtin.py` avec :

- un nom stable ;
- une description courte ;
- un schéma JSON strict ;
- une fonction recevant les arguments sous forme de dictionnaire.

Enregistrez-le ensuite dans `build_default_registry`. Le registre refuse les noms
inconnus et transforme toute exception en résultat structuré.

## Ajouter un fournisseur

Implémentez le protocole `Provider` de `providers/base.py`. Une réponse contient du
texte, zéro ou plusieurs `ToolCall`, et éventuellement un jeton de continuation.
Ajoutez enfin le fournisseur dans `providers/factory.py`.

## Format d'un scénario

```json
{
  "name": "nom_unique",
  "input": "question envoyée au harness",
  "must_contain": ["fragment attendu"],
  "must_not_contain": ["fragment interdit"],
  "min_length": 20
}
```

