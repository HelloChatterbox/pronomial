import unittest
from pronomial import replace_corefs, detect_nouns, score_corefs, word_tokenize


class TestCorefEN(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lang = "en"
        self.maxDiff = None

    def test_female(self):
        self.assertEqual(
            replace_corefs("Inês said she loves me!"),
            "Inês said Inês loves me !"
        )
        self.assertEqual(
            replace_corefs("Bob threatened to kill Alice to make her pay "
                           "her debts"),
            "Bob threatened to kill Alice to make Alice pay Alice debts"
        )
        self.assertEqual(
            replace_corefs(
                "Janet has a husband, Bob, and one son, Sam. "
                "A second child was stillborn in November 2009, causing her "
                "to miss Bristol City's match against Nottingham Forest. "
                "City manager Gary Johnson dedicated their equalising goal "
                "in the match to Janet, who had sent a message of support to her teammates."),
            "Janet has a husband , Bob , and one son , Sam . "
            "A second child was stillborn in November 2009 , causing Janet to miss Bristol City 's match against Nottingham Forest . "
            "City manager Gary Johnson dedicated their equalising goal in the match to Janet , "
            "Janet had sent a message of support to Janet teammates .")

    def test_male(self):
        self.assertEqual(
            replace_corefs("Joe was talking to Bob and told him to go home "
                           "because he was drunk"),
            "Joe was talking to Bob and told Bob to go home because Bob was drunk"
        )
        self.assertEqual(
            replace_corefs("Jack is one of the top candidates in "
                           "the elections. His ideas are unique compared to "
                           "Bob's."),
            "Jack is one of the top candidates in the elections . Jack ideas are unique compared to Bob 's ."
        )
        self.assertEqual(
            replace_corefs("I voted for Elon because he is clear about his "
                           "values. His ideas represent a majority of the "
                           "nation. He is better than Jack."),
            "I voted for Elon because Elon is clear about Elon values ."
            " Elon ideas represent a majority of the nation ."
            " Elon is better than Jack ."
        )

    def test_plural(self):
        self.assertEqual(
            replace_corefs(
                "Members voted for John because they see him as a good leader."),
            "Members voted for John because Members see John as a good leader ."
        )
        self.assertEqual(
            replace_corefs(
                "Leaders around the world say they stand for peace."),
            "Leaders around the world say Leaders stand for peace ."
        )
        self.assertEqual(
            replace_corefs(
                "I have many friends. They are an important part of my life."),
            "I have many friends . friends are an important part of my life ."
        )
        # they + it
        self.assertEqual(
            replace_corefs(
                "My neighbours just adopted a puppy. They care for it like a baby."),
            "My neighbours just adopted a puppy . neighbours care for puppy like a baby ."
        )

        # merging of previous Nouns (limited to 2 names total)
        self.assertEqual(
            replace_corefs("Alice invited Marcia to go with her to "
                           "their favorite store"),
            "Alice invited Marcia to go with Alice to their "
            "favorite store"
        )

    def test_it(self):
        self.assertEqual(
            replace_corefs("My neighbors have a cat. It has a bushy tail."),
            "My neighbors have a cat . cat has a bushy tail ."
        )
        self.assertEqual(
            replace_corefs("Here is the book now take it."),
            "Here is the book now take book ."
        )
        # dog -> neutral
        self.assertEqual(
            replace_corefs("dog is man's best friend. It is always loyal."),
            "dog is man 's best friend . dog is always loyal ."
        )
        # Dog -> name (male)
        self.assertEqual(
            replace_corefs("Dog is man's best friend. It is always loyal."),
            "Dog is man 's best friend . Dog is always loyal ."
        )
        self.assertEqual(
            replace_corefs("is the light turned on? turn it off"),
            "is the light turned on ? turn light off"
        )
        self.assertEqual(
            replace_corefs("Turn off the light and change it to blue"),
            "Turn off the light and change light to blue"
        )

        # it + who
        self.assertEqual(
            replace_corefs(
                "London is the capital and most populous city of England and the United Kingdom. "
                "Standing on the River Thames in the south east of the island of Great Britain, "
                "London has been a major settlement for two millennia. "
                "It was founded by the Romans, who named it Londinium."),
            "London is the capital and most populous city of England and the United Kingdom . "
            "Standing on the River Thames in the south east of the island of Great Britain , "
            "London has been a major settlement for two millennia . "
            "London was founded by the Romans , Romans named London Londinium ."
        )

    def test_dictionary_words(self):
        # harcoded wordlists that map words to gendered pronouns
        # boy -> male
        self.assertEqual(
            replace_corefs(
                "The sign was too far away for the boy to read it."),
            "The sign was too far away for the boy to read sign ."
        )
        # girl -> female
        self.assertEqual(
            replace_corefs("The girl said she would take the trash out."),
            "The girl said girl would take the trash out ."
        )
        # mom -> female
        self.assertEqual(
            replace_corefs("call Mom. tell her to buy eggs. tell her to buy "
                           "coffee. tell her to buy milk"),
            "call Mom . tell Mom to buy eggs . tell Mom to buy coffee . tell Mom to buy milk"
        )
        # dad -> male
        self.assertEqual(
            replace_corefs("call dad. tell him to buy bacon. tell him to buy "
                           "coffee. tell him to buy beer"),
            "call dad . tell dad to buy bacon . tell dad to buy coffee . tell dad to buy beer"
        )

    def test_hardcoded_postag_fixes(self):
        # "turn on" falsely detected as ('Turn', 'NN'), ('on', 'IN')
        # "change it" falsely detected as ('change', 'NN'), ('it', 'PRP')
        # these specific cases are corrected manually when detected
        self.assertEqual(
            replace_corefs("Turn on the light and change it to blue"),
            "Turn on the light and change light to blue"
        )

    def test_mixed(self):
        self.assertEqual(
            replace_corefs("My sister has a dog, She loves him!"),
            "My sister has a dog , sister loves dog !"
        )
        self.assertEqual(
            replace_corefs(
                "A short while later, Michael decided that he wanted to play a role in his son's life, and tried to get Lisa to marry him, but by this time, she wanted nothing to do with him. "
                "Around the same time, Lisa's son Tom had returned from Vietnam with a drug habit. One night, Michael caught Tom breaking into his office to steal drugs"
            ),
            "A short while later , Michael decided that Michael wanted to play a role in Michael son 's life , and tried to get Lisa to marry Michael , but by this time , Lisa wanted nothing to do with Michael . "
            "Around the same time , Lisa 's son Tom had returned from Vietnam with a drug habit . One night , Michael caught Tom breaking into Michael office to steal drugs"
        )

    def test_neutral_postag(self):
        # in {noun}-> in == IN -> {noun} == neutral

        # "Arendelle" is recognized as a location because of "in", otherwise
        # it would be tagged as a female name and be used instead of Elsa
        self.assertEqual(
            replace_corefs(
                "Chris is very handsome. He is Australian. Elsa lives in Arendelle. He likes her."),
            "Chris is very handsome . Chris is Australian . Elsa lives in Arendelle . Chris likes Elsa ."
        )

    def test_in(self):
        # "into/in his/her/their" will select first male/female/plural noun
        # instead of last
        self.assertEqual(
            replace_corefs("One night, Michael caught Tom in his office"),
            "One night , Michael caught Tom in Michael office"
        )
        self.assertEqual(
            replace_corefs(
                "One night, Michael caught Tom breaking into his office"),
            "One night , Michael caught Tom breaking into Michael office"
        )

    def test_with(self):
        # "with her/him/them" will select first male/female/plural noun
        # instead of last seen
        self.assertEqual(
            replace_corefs("Kevin invited Bob to go with him to "
                           "his favorite fishing spot"),
            "Kevin invited Bob to go with Kevin to Kevin favorite fishing spot"
        )
        self.assertEqual(
            replace_corefs("Alice invited Marcia to go with her"),
            "Alice invited Marcia to go with Alice"
        )

        self.assertEqual(
            replace_corefs("The Martians invited the Venusians to go with "
                           "them to Pluto"),
            "The Martians invited the Venusians to go with Martians to Pluto"
        )

    def test_that(self):
        # "that her/he/they" will select first male/female/plural noun
        # instead of last seen
        self.assertEqual(
            replace_corefs(
                "Bob telephoned Jake to tell him that he lost the laptop."),
            "Bob telephoned Jake to tell Jake that Bob lost the laptop ."
        )
        self.assertEqual(
            replace_corefs("Ana telephoned Alice to tell her that she lost "
                           "the bus"),
            "Ana telephoned Alice to tell Alice that Ana lost the bus"
        )
        self.assertEqual(
            replace_corefs("The Martians told the Venusians that they used "
                           "to have an ocean"),
            "The Martians told the Venusians that Martians used to have an ocean"
        )

    def test_capitalization_ambiguity(self):
        # capitalization mistakes
        # Cat with upper case is tagged as a male name, works as expected
        self.assertEqual(
            replace_corefs(
                "My neighbors have a Cat. It has a bushy tail. They love him!"),
            "My neighbors have a Cat . Cat has a bushy tail . neighbors love Cat !"
        )

        # cat with lower case is not gender classified and not selected to
        # replace "him", tail is wrongly selected because it is the closest
        # noun
        self.assertEqual(
            replace_corefs("My neighbors have a cat. It has a bushy tail. "
                           "They love him!"),
            "My neighbors have a cat . cat has a bushy tail . neighbors love tail !"
            # ... neighbors love cat ...
        )

    def test_ambiguous(self):
        # a little ambiguous results, unexpected but technically acceptable
        self.assertEqual(
            replace_corefs("the dudes were talking with their enemies and "
                           "they decided to avoid war"),
            "the dudes were talking with dudes enemies and enemies decided to avoid war"
            # ... and dudes decided ...
        )
        self.assertEqual(
            replace_corefs(
                "One night, Michael caught Tom breaking into his office to steal drugs, and he used this information to blackmail Lisa into marrying him."),
            "One night , Michael caught Tom breaking into Michael office to steal drugs , and Michael used this information to blackmail Lisa into marrying Tom ."
            # ... blackmail Lisa into marrying Michael ."
        )

    def test_gender_failures(self):
        ## gender misclassifications
        # NOTE Sproule is misclassified as female
        self.assertEqual(
            replace_corefs(
                "Janet has a husband, Sproule, and one son, Sam. "
                "A second child was stillborn in November 2009, causing her "
                "to miss Bristol City's match against Nottingham Forest. "
                "City manager Gary Johnson dedicated their equalising goal "
                "in the match to Janet, who had sent a message of support to her teammates."),
            "Janet has a husband , Sproule , and one son , Sam . "
            "A second child was stillborn in November 2009 , causing Sproule to miss Bristol City 's match against Nottingham Forest . "
            "City manager Gary Johnson dedicated their equalising goal in the match to Janet , "
            "Janet had sent a message of support to Janet teammates .")
        #  "... causing Janet to miss ..."

        # "his" and "him" are not properly replaced because Sproule is misclassified as female
        self.assertEqual(
            replace_corefs(
                "Sproule has a wife, Janet, and one son, Sam. "
                "A second child was stillborn in November 2009, causing him to miss Bristol City's match against Nottingham Forest. "
                "City manager Gary Johnson dedicated their equalising goal in the match to Sproule, who had sent a message of support to his teammates."),
            "Sproule has a wife , Janet , and one son , Sam . "
            "A second child was stillborn in November 2009 , causing Sam to miss Bristol City 's match against Nottingham Forest . "
            "City manager Gary Johnson dedicated their equalising goal in the match to Sproule , Sproule had sent a message of support to Johnson teammates .")
        #  "... causing Sproule to miss ... to Sproule teammates"

    def test_detect_nouns(self):
        tokens = ['London', 'has', 'been', 'a', 'major', 'settlement', 'for',
                  'two', 'millennia', '.', 'It', 'was', 'founded', 'by', 'the',
                  'Romans', ',', 'who', 'named', 'it', 'Londinium', '.']
        self.assertEqual(
            detect_nouns(tokens, lang="en"),
            {'female': [],
             'first': [],
             'male': [0, 20],
             'neutral': [0, 5, 8, 20],
             'plural': [15],
             'subject': [0, 5, 8, 20],
             'verb_subject': [0],
             "tokens": tokens})
        self.assertEqual(
            detect_nouns(tokens, lang="en", return_idx=False),
            {'female': [],
             'first': [],
             'male': ['London', 'Londinium'],
             'neutral': ['London', 'settlement', 'millennia', 'Londinium'],
             'plural': ['Romans'],
             'subject': ['London', 'settlement', 'millennia', 'Londinium'],
             'verb_subject': ['London'],
             "tokens": tokens})

    def test_coreferences(self):

        # word indexes are used internally, but to make these tests human
        # friendly we are comparing actual words, note that in practice we
        # should work with token indexes
        def test_prediction(sentence, expected):
            tokens = word_tokenize(sentence)
            pred = score_corefs(sentence, lang="en")
            matches = []
            for tok_idx, match in pred.items():
                tok = tokens[tok_idx]
                for tok2_idx, score in match.items():
                    tok2 = tokens[tok2_idx]
                    matches.append((tok, tok2, score))
            self.assertEqual(matches, expected)

        test_prediction(
            "London has been a major settlement for two millennia. It was founded by the Romans, who named it Londinium.",
            [('It', 'London', 0.43478260869565216),
             ('It', 'settlement', 0.2608695652173913),
             ('It', 'millennia', 0.30434782608695654),
             ('who', 'settlement', 0.07692307692307693),
             ('who', 'millennia', 0.15384615384615385),
             ('who', 'Romans', 0.7692307692307693),
             ('it', 'London', 0.43478260869565216),
             ('it', 'settlement', 0.2608695652173913),
             ('it', 'millennia', 0.30434782608695654)]
            )
        test_prediction(
            "Joe was talking to Bob and told him to go home because he was drunk",
            [('him', 'Joe', 0.45454545454545453),
             ('him', 'Bob', 0.5454545454545454),
             ('he', 'Joe', 0.4166666666666667),
             ('he', 'Bob', 0.5),
             ('he', 'home', 0.08333333333333333)]
            )
        test_prediction("My neighbors have a Cat. It has a bushy tail. They "
                        "love him!",
                        [('It', 'Cat', 1.0),
                         ('They', 'neighbors', 1.0),
                         ('him', 'Cat', 0.9090909090909091),
                         ('him', 'tail', 0.09090909090909091)]
                        )
        test_prediction("dog is man's best friend. It is always loyal.",
                        [('It', 'dog', 0.43478260869565216),
                         ('It', 'man', 0.2608695652173913),
                         ('It', 'friend', 0.30434782608695654)]
                        )
        test_prediction("The sign was too far away for the boy to read it.",
                        [('it', 'sign', 0.625),
                         ('it', 'boy', 0.375)]
                        )
        test_prediction("call dad. tell him to buy bacon. tell him to buy "
                        "coffee. tell him to buy beer",
                        [('him', 'dad', 1.0),
                         ('him', 'dad', 0.8461538461538461),
                         ('him', 'bacon', 0.15384615384615385),
                         ('him', 'dad', 0.6875),
                         ('him', 'bacon', 0.125),
                         ('him', 'coffee', 0.1875)]
                        )
        test_prediction(
            "the dudes were talking with their enemies and they decided to avoid war",
            [('their', 'dudes', 1.0),
             ('they', 'dudes', 0.47619047619047616),
             ('they', 'enemies', 0.5238095238095238)]
            )
