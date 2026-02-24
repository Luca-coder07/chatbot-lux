import json
import difflib
import sys
import os
from datetime import datetime
from typing import Optional, Any, Dict, List, Tuple

class IntelligentChatbot:
    def __init__(self, json_files: Optional[List[str]] = None, learn_mode: bool = False) -> None:
        if json_files is None:
            json_files = ["knowledge.json"]
        self.json_files = json_files if isinstance(json_files, list) else [json_files]
        self.learn_mode = learn_mode
        self.knowledge = self.load_all_knowledge()
        self.stats = self.load_stats()
        self.question_counter = 0
        self.auto_save_interval = 5
        # Cache for lowercased questions to avoid recreating on every query
        self._questions_lower_cache: List[str] = []
        self._update_questions_cache()

    def load_all_knowledge(self) -> List[Dict[str, Any]]:
        """Charge et fusionne tous les fichiers JSON"""
        all_knowledge = []

        for json_file in self.json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Gérer différents formats possibles
                    if "qa_pairs" in data:
                        all_knowledge.extend(data["qa_pairs"])
                    elif isinstance(data, list):
                        all_knowledge.extend(data)
                    else:
                        print(f"⚠️ Format inconnu dans {json_file}")
            except FileNotFoundError:
                print(f"⚠️ Fichier {json_file} non trouvé - création à la sauvegarde")
                # Créer le fichier vide
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump({"qa_pairs": []}, f, ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                print(f"⚠️ Erreur de lecture dans {json_file}")
            
        print(f"📚 Chargé {len(all_knowledge)} entrées depuis {len(self.json_files)} fichier(s)")
        return all_knowledge
    
    def _update_questions_cache(self) -> None:
        """Updates the cached list of lowercased questions for faster matching."""
        self._questions_lower_cache = [item["q"].lower() for item in self.knowledge]
    
    def _auto_save_if_needed(self) -> None:
        """Performs auto-save of knowledge and statistics if threshold is reached."""
        if self.question_counter % self.auto_save_interval == 0:
            self.save_knowledge()
            self.save_stats()
            print(f"💾 Auto_save: {self.question_counter} questions traitées")
        
    
    def load_knowledge(self) -> List[Dict[str, Any]]:
        """Charge les connaissances depuis le fichier JSON"""
        try:
            with open(self.json_files, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data["qa_pairs"]
        except FileNotFoundError:
            # Si le fichier n'existe pas, on crée une structure vide
            return []
        except json.JSONDecodeError:
            print(f"⚠️  Erreur : Le fichier {self.json_files} est corrompu.")
            return []
    
    def save_knowledge(self) -> None:
        """Sauvegarde les connaissances dans le fichier JSON"""
        primary_file = self.json_files[0]

        with open(primary_file, 'w', encoding='utf-8') as f:
            json.dump({"qa_pairs": self.knowledge}, f, ensure_ascii=False, indent=4)

        if len(self.json_files) > 1 and self.learn_mode:
            print(f"💾 Sauvegarde principale dans {primary_file}")
            print(f"   (Les autres fichiers sont en lecteur seule)")

    def load_stats(self) -> Dict[str, Any]:
        """Charge ou crée le fichier de stats d'apprentissage"""
        stats_file = "stats_file.json"
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Structure initiale des stats
            stats_init = {
                "total_questions": 0,
                "relevant_answers": 0,
                "irrelevant_answers": 0,
                "new_learnings": 0,
                "history": []
            }
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_init, f, ensure_ascii=False, indent=4)
            return stats_init
    
    def save_stats(self) -> None:
        """Sauvegarde les stats d'apprentissage"""
        with open("stats_file.json", 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=4)
    
    def find_answer(self, question: str) -> Tuple[Optional[str], float]:
        """Trouve la réponse la plus pertinente"""
        self.question_counter += 1

        self.stats["total_questions"] += 1
        
        if not self.knowledge:
            return "Je n'ai aucune connaissance pour l'instant. En mode --learn, vous pouvez m'apprendre des choses !", 0.0
        
        # Use cached lowercased questions instead of recreating on every call
        
        # Recherche avec différents seuils de similarité
        lower_question = question.lower()
        
        # 1. Correspondance exacte (score 100%)
        for item in self.knowledge:
            if item["q"].lower() == lower_question:
                self.stats["relevant_answers"] += 1
                return item["a"], 1.0
        
        # 2. Correspondance approximative (threshold variable selon le mode)
        threshold = 0.5 if self.learn_mode else 0.7  # Plus permissif en mode apprentissage
        nearest_question = difflib.get_close_matches(
            lower_question, 
            self._questions_lower_cache, 
            n=1, 
            cutoff=threshold
        )
        
        if nearest_question:
            for item in self.knowledge:
                if item["q"].lower() == nearest_question[0]:
                    # Calculer un score de pertinence
                    score = difflib.SequenceMatcher(None, lower_question, nearest_question[0]).ratio()
                    self.stats["relevant_answers"] += 1

                    self._auto_save_if_needed()
                    
                    return item["a"], score
        
        # Aucune correspondance trouvée
        self.stats["irrelevant_answers"] += 1
        
        self._auto_save_if_needed()

        return None, 0.0
    
    def learn_new_answer(self, question: str, answer: str, rating: Optional[int] = None, source_file: Optional[str] = None) -> bool:
        """Apprend une nouvelle question/réponse"""
        # Vérifier si la question existe déjà
        for i, item in enumerate(self.knowledge):
            if item["q"].lower() == question.lower():
                if rating and rating > 7:  # Si la réponse était bonne, on ne change rien
                    return False
                print(f"\n⚠️ Question déjà existante")
                choice = input("   Voulez-vous la remplacer ? (o/n) : ").lower()
                if choice == 'o':
                    self.knowledge[i] = {
                        "q": question,
                        "a": answer,
                        "learned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": source_file or self.json_files[0]
                    }
                    self.save_knowledge()
                    self._update_questions_cache()  # Update cache after modification
                    return True
                return False
        
        # Nouvelle question
        self.knowledge.append({
            "q": question,
            "a": answer,
            "learned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source_file or self.json_files[0]
        })
        self.stats["new_learnings"] += 1
        self.save_knowledge()
        self._update_questions_cache()  # Update cache after adding new knowledge
        return True
    
    def evaluate_relevance(self, question: str, found_answer: str, score: float) -> None:
        """Évalue la pertinence de la réponse et ajuste l'apprentissage"""
        print(f"\n📊 Score de pertinence : {score:.2%}")
        
        if self.learn_mode and score < 0.8:  # En mode apprentissage, on demande toujours un feedback
            print("\n🔍 Mode apprentissage actif - Aidez-moi à m'améliorer !")
            rating = input("   Notez la pertinence de cette réponse (1-10) : ")
            
            try:
                rating = int(rating)
                if rating < 5:  # Mauvais réponse
                    print("   🤔 Désolé ! Pouvez-vous me donner la bonne réponse ?")
                    good_answer = input("   La bonne réponse est : ")
                    if good_answer:
                        self.learn_new_answer(question, good_answer, rating)
                        self.stats["history"].append({
                            "q": question,
                            "ancienne_reponse": found_answer,
                            "rating": rating,
                            "amelioration": True
                        })
                elif rating > 8:  # Bonne réponse
                    print("   👍 Super ! Je rating que cette réponse est pertinente.")
                    self.stats["history"].append({
                        "q": question,
                        "rating": rating,
                        "relevant": True
                    })
            except ValueError:
                pass
            
            self.save_stats()
    
    def display_stats(self) -> None:
        """Affiche les stats d'apprentissage"""
        print("\n" + "="*60)
        print("📈 STATISTIQUES D'APPRENTISSAGE")
        print("="*60)
        print(f"📊 Questions totales : {self.stats['total_questions']}")
        print(f"✅ Réponses pertinentes : {self.stats['relevant_answers']}")
        print(f"❌ Réponses non pertinentes : {self.stats['irrelevant_answers']}")
        
        if self.stats['total_questions'] > 0:
            taux_pertinence = (self.stats['relevant_answers'] / self.stats['total_questions']) * 100
            print(f"🎯 Taux de pertinence : {taux_pertinence:.1f}%")
        
        print(f"📚 Nouveaux apprentissages : {self.stats['new_learnings']}")
        print(f"📁 Base de connaissances : {len(self.knowledge)} entrées")
        print("="*60)

def main() -> None:
    """Fonction principale avec gestion des flags"""
    # Analyser les arguments de la ligne de commande
    learn_mode = "--learn" in sys.argv
    
    print("="*60)
    print("🤖 CHATBOT INTELLIGENT")
    print("="*60)
    
    if learn_mode:
        print("🌟 MODE APPRENTISSAGE ACTIVÉ")
        print("   Je vais apprendre de nos conversations !")
    else:
        print("💬 MODE NORMAL")
        print("   Utilisez --learn au lancement pour activer le mode apprentissage")
    
    print("="*60)
    print("Commandes spéciales :")
    print("  /sources   - Voir les fichiers sources")
    print("  /count     - Afficher le nombre de question(s) traitées")
    print("  /stats     - Afficher les stats")
    print("  /save      - Sauvegarder manuellement")
    print("  /quit      - Quitter")
    print("="*60)
    
    # Initialiser le chatbot with all knowledge sources
    chatbot = IntelligentChatbot(
        json_files=[
            "knowledge_base.json",  # Primary knowledge base (read/write)
            "personality.json",      # Personality traits and behaviors
            "facts.json",            # Interesting facts and trivia
            "faq.json",              # Frequently asked questions
            "general_knowledge.json",# General educational knowledge
            "python_tips.json"       # Python programming tips
        ],
        learn_mode=learn_mode
    )
    
    while True:
        question = input("\n🧑 Vous : ").strip()
        
        # Commandes spéciales
        if question.lower() == '/quit':
            print("\n👋 Chatbot : Au revoir !")
            chatbot.display_stats()
            break
        elif question.lower() == '/stats':
            chatbot.display_stats()
            continue
        elif question.lower() == '/save':
            chatbot.save_knowledge()
            print("💾 Connaissances sauvegardées !")
            continue
        elif question.lower() == '/count':
            print(f"📊 Questions traitées : {chatbot.question_counter}")
            continue
        elif question.lower() == '/sources':
            print(f"\n📁 Fichiers sources chargés: ")
            for i, f in enumerate(chatbot.json_files, 1):
                count = sum(1 for item in chatbot.knowledge if item.get('source') == f)
                print(f"  {i}. {f} : {count} entrées")
        
        if not question:
            continue
        
        # Chercher la réponse
        result = chatbot.find_answer(question)
        
        if result[0] is not None:
            answer, score = result
            print(f"🤖 Chatbot : {answer}")
            
            # Évaluer la pertinence (surtout en mode learn)
            chatbot.evaluate_relevance(question, answer, score)
        else:
            print("🤖 Chatbot : Je ne sais pas répondre à cette question.")
            
            if learn_mode:
                print("   🌟 Mode apprentissage : Enseignez-moi la réponse !")
                new_answer = input("   Quelle devrait être la réponse ? (ou 'skip' pour passer) : ")
                
                if new_answer.lower() != 'skip':
                    if chatbot.learn_new_answer(question, new_answer):
                        print("   ✅ J'ai appris cette nouvelle information !")
                        # Maintenant qu'on a appris, on peut répondre correctement
                        learned_answer, _ = chatbot.find_answer(question)
                        print(f"   🤔 Maintenant je répondrais : {learned_answer}")
                    else:
                        print("   ⚠️  Cette question existe déjà dans ma base.")

if __name__ == "__main__":
    main()