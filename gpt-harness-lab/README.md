# GPT Harness Lab

Un mini-projet Python pour comprendre ce qui entoure un modèle GPT : prompts,
mémoire, outils locaux, traces et évaluations. Le projet fonctionne immédiatement
en mode `mock`, sans clé API et sans dépendance externe.

## Démarrage rapide

```bash
cd gpt-harness-lab
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
python -m pip install -e .
gpt-harness ask "Calcule 12 * (3 + 2)"
gpt-harness chat
gpt-harness eval scenarios/demo.json
```

On peut aussi lancer sans installation :

```bash
PYTHONPATH=src python -m gpt_harness ask "Bonjour"
```

## Utiliser OpenAI

Installez l'extra, fournissez la clé dans l'environnement, puis sélectionnez le
fournisseur. Le modèle reste configurable dans `configs/default.toml` ou avec
`GPT_HARNESS_MODEL`.

```bash
python -m pip install -e ".[openai]"
export OPENAI_API_KEY="..."
export GPT_HARNESS_PROVIDER=openai
gpt-harness ask "Résume en trois points le rôle d'un harness GPT."
```

Le fournisseur OpenAI utilise la Responses API. Lorsqu'un modèle demande un outil,
le harness exécute la fonction locale, renvoie son résultat au modèle, puis continue
jusqu'à obtenir une réponse finale ou atteindre la limite configurée.

## Commandes

```text
gpt-harness ask TEXT             Une requête unique
gpt-harness chat                 Une conversation interactive
gpt-harness eval FICHIER         Exécute un jeu de scénarios JSON
gpt-harness prompts list         Liste les fichiers .gpt
gpt-harness prompts show NOM     Affiche un prompt
```

Options globales : `--config`, `--provider`, `--model` et `--no-trace`.

## Arborescence

```text
configs/       Configuration TOML
docs/          Architecture et guides
examples/      Exemple d'intégration Python
prompts/       Prompts composables au format .gpt
scenarios/     Jeux d'évaluation JSON
scripts/       Commandes de démonstration
src/           Package gpt_harness
tests/         Tests unitaires sans réseau
```

Consultez [docs/architecture.md](docs/architecture.md) pour le flux interne et
[docs/customization.md](docs/customization.md) pour ajouter un outil, un prompt ou
un fournisseur.

