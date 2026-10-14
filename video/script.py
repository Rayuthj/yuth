"""Narration script for "What If You Had 500 IQ?".

The script is split into sentence-level *beats*. Each beat is synthesized
separately so the animation can be synchronized to individual lines.

Beat fields:
    id     unique id, used by chapter modules to anchor shots
    text   the spoken line
    voice  speaker key (see VOICES); defaults to the narrator
    gap    relative weight of the pause placed *before* this beat when the
           timeline distributes slack time inside a chapter
"""

# Kokoro voice ids per speaker.
VOICES = {
    "narrator": "af_heart",
    "hero": "am_michael",
    "friend": "am_puck",
    "friend2": "bf_emma",
}

# (number, title, start_seconds, end_seconds)
CHAPTER_SLOTS = [
    (1, "The Hook", 0, 40),
    (2, "The First 24 Hours", 40, 100),
    (3, "Your Brain Becomes a Supercomputer", 100, 160),
    (4, "You Can Predict People", 160, 220),
    (5, "You Could Change the World", 220, 290),
    (6, "The Dark Side of Extreme Intelligence", 290, 350),
    (7, "Could You Invent the Future?", 350, 410),
    (8, "The Biggest Problem: Other People", 410, 470),
    (9, "What Would Happen to Your Life?", 470, 540),
    (10, "The Final Revelation", 540, 600),
]

# Per-chapter timing hints for the timeline fitter:
#   lead  seconds before the first line (sound design / establishing shot)
#   tail  seconds after the last line (transition, title card, end card)
CHAPTER_TIMING = {
    1: dict(lead=1.0, tail=2.3),
    2: dict(lead=1.0, tail=1.6),
    3: dict(lead=1.0, tail=1.4),
    4: dict(lead=1.0, tail=1.4),
    5: dict(lead=1.0, tail=1.6),
    6: dict(lead=1.6, tail=1.6),
    7: dict(lead=1.0, tail=1.4),
    8: dict(lead=1.0, tail=1.4),
    9: dict(lead=1.0, tail=2.0),
    10: dict(lead=0.8, tail=7.6),
}


def B(id, text, voice="narrator", gap=1.0):
    return dict(id=id, text=text, voice=voice, gap=gap)


BEATS = {
    1: [
        B("c1_01", "Imagine waking up tomorrow with a brain so powerful that every problem you've ever struggled with suddenly looks ridiculously easy."),
        B("c1_02", "Mathematics? Effortless."),
        B("c1_03", "Languages? Instantly understandable."),
        B("c1_04", "Human behavior? You start noticing patterns nobody else seems to see."),
        B("c1_05", "You can connect ideas across science, psychology, technology, and history at incredible speed."),
        B("c1_06", "Now imagine your intelligence is so far beyond anything humans have ever demonstrated that ordinary life begins to feel completely different.", gap=1.5),
        B("c1_07", "We're talking about a hypothetical IQ of 500."),
        B("c1_08", "But here's the real question:", gap=1.5),
        B("c1_09", "Would you become the smartest person alive... or would your own mind become your biggest problem?"),
    ],
    2: [
        B("c2_01", "Hour one. The alarm rings... and something feels different."),
        B("c2_02", "The ticking clock isn't just noise anymore. It's a rhythm, with patterns inside patterns."),
        B("c2_03", "Your phone, the traffic outside, the books on your shelf... suddenly, everything seems connected."),
        B("c2_04", "By lunch, you've solved a Sudoku and a Rubik's cube, before your toast even pops."),
        B("c2_05", "But let's be honest.", gap=2.0),
        B("c2_06", "IQ tests are designed so the average score is 100, and most can't measure much past 160."),
        B("c2_07", "A score of 500 is pure science fiction... which is exactly what makes it fun to imagine."),
        B("c2_08", "And even here, a powerful brain doesn't mean perfect memory, instant knowledge, or superpowers. You still have to read the book."),
        B("c2_09", "What changes is how fast you reason, learn, and connect ideas."),
        B("c2_10", "And as the sun sets, you realize the world is full of questions nobody has answered yet.", gap=1.5),
    ],
    3: [
        B("c3_01", "Day two: school."),
        B("c3_02", "Your teacher writes a monster equation on the board. The whole class groans."),
        B("c3_03", "But you don't see symbols. You see shapes, pieces that move, fit together, and simplify, like a puzzle solving itself."),
        B("c3_04", "In the lab, you spot a pattern hiding in messy data."),
        B("c3_05", "On a computer, you hold an entire program in your head and find the bug in seconds."),
        B("c3_06", "Your mind becomes a giant web, where biology links to math, and history links to technology."),
        B("c3_06b", "You still have to study, but new subjects click in days instead of months."),
        B("c3_07", "But here's the catch. A brilliant idea is only a guess... until you test it.", gap=1.5),
        B("c3_08", "Real science still needs experiments, evidence, data, other people checking your work, and time. Nature doesn't care how smart you are."),
        B("c3_09", "Still, walking home, you imagine a machine that could crack problems everyone calls impossible.", gap=1.5),
    ],
    4: [
        B("c4_01", "Then you step into the city, and things get interesting."),
        B("c4_02", "People aren't random. They follow habits, incentives, and routines."),
        B("c4_03", "That man checking his watch? Probably running late."),
        B("c4_04", "The woman staring at the menu? She's about to change her order."),
        B("c4_05", "You can even see how one tiny choice, like someone stopping to tie a shoe, ripples outward into something bigger."),
        B("c4_06", "For a moment, it feels like you can read the future."),
        B("c4_07", "Then the guy you were sure would turn left... does a little dance and goes right.", gap=1.3),
        B("c4_08", "Patterns can improve your guesses, but a guess is still just a probability. People aren't equations, and nobody, no matter how smart, can read minds."),
        B("c4_09", "Just ask your best friend."),
        B("c4_10", "I know exactly what you're about to say.", voice="hero"),
        B("c4_11", "Do penguins have knees?", voice="friend", gap=1.5),
        B("c4_12", "Didn't see that one coming. For the record... they do.", gap=2.0),
    ],
    5: [
        B("c5_01", "So you decide to aim higher. Much higher."),
        B("c5_02", "Cleaner energy: better solar panels, and power grids that waste less electricity."),
        B("c5_03", "Medical research, to understand diseases and design better treatments."),
        B("c5_04", "Smarter transportation, with better routes and fewer traffic jams."),
        B("c5_05", "Climate models that show how our planet is changing."),
        B("c5_06", "Learning tools that adapt to the way each student actually learns."),
        B("c5_07", "Making sure powerful AI systems actually do what people intend."),
        B("c5_08", "And a few famous unsolved math problems, just for fun."),
        B("c5_09", "Your notebook fills up in record time. So does your coffee mug."),
        B("c5_10", "But then, reality knocks on the door.", gap=1.8),
        B("c5_11", "An idea isn't a power plant. A formula isn't a medicine. Ideas have to be tested, funded, built, checked for safety and ethics, and explained to the people they'll affect."),
        B("c5_12", "So, one by one, others join you. An engineer. A doctor. A teacher. A programmer."),
        B("c5_13", "And you realize that even the smartest person on Earth can't build a better world alone.", gap=1.3),
    ],
    6: [
        B("c6_01", "But every story has a darker side."),
        B("c6_02", "Remember, this part is fiction. Research doesn't show that high intelligence makes people unhappy."),
        B("c6_03", "But in our story, your room slowly fills with equations and unfinished projects."),
        B("c6_04", "Simple choices become enormous. Should you go outside? What could happen? What evidence is missing?"),
        B("c6_05", "Every option splits into ten more... and then a hundred."),
        B("c6_06", "It's frustrating when others don't share your interests, and explaining your ideas feels like translating an alien language."),
        B("c6_07", "You expect perfection from yourself, every single time."),
        B("c6_08", "And there's a trap: believing that being intelligent automatically makes you wise.", gap=1.3),
        B("c6_09", "So you do the smartest thing all week. You close the notebook, go for a walk, and call a friend.", gap=2.0),
        B("c6_10", "Because even a brilliant mind still needs fresh air, sleep, and people who care."),
    ],
    7: [
        B("c7_01", "With a clearer head, you start imagining the future. Not science fiction... well, maybe a little."),
        B("c7_02", "Medical scanners that might spot diseases years earlier than today."),
        B("c7_03", "New materials, lighter than plastic, and stronger than steel."),
        B("c7_04", "Batteries that store far more energy."),
        B("c7_05", "AI assistants that help scientists test thousands of ideas."),
        B("c7_06", "New ways to explore the universe, from smarter telescopes to tiny space probes."),
        B("c7_07", "But none of this is guaranteed. Inventions depend on knowledge, tools, experiments... and the laws of physics, which don't bend for anyone.", gap=1.5),
        B("c7_08", "So you build a prototype: a delivery drone."),
        B("c7_09", "Test one: it spins in circles. Test two: it flips over and lands in a bush."),
        B("c7_10", "So you study what went wrong, change the design, and test again."),
        B("c7_11", "Test three... it flies.", gap=1.3),
        B("c7_12", "Because even brilliant ideas have to survive contact with reality.", gap=1.3),
    ],
    8: [
        B("c8_01", "Here's the problem nobody warns geniuses about: other people."),
        B("c8_02", "You gather your friends to explain your newest idea."),
        B("c8_03", "So, if we map the feedback loop onto a nonlinear probability space, then the recursive variables...", voice="hero"),
        B("c8_04", "Ten minutes later, the diagram has taken over the room... and one friend is asleep."),
        B("c8_05", "Can you say that... in normal words?", voice="friend2"),
        B("c8_06", "So you try again. One simple drawing: a snowball rolling downhill, getting bigger."),
        B("c8_07", "Small changes can grow into huge ones.", voice="hero"),
        B("c8_08", "Oh! Why didn't you just say that?", voice="friend"),
        B("c8_09", "Understanding something and explaining it are two different skills.", gap=1.3),
        B("c8_10", "So you learn to listen, to ask questions, and to work with people whose strengths are different from yours: the artist, the organizer, the friend who just gets people."),
        B("c8_11", "Creativity, empathy, patience, and teamwork aren't extras. They're part of being smart."),
    ],
    9: [
        B("c9_01", "Now, fast-forward through your life."),
        B("c9_02", "At first, you're obsessed with learning. Books, languages, physics, music... you devour everything."),
        B("c9_03", "Then you start using it to help people solve real problems: a broken water pump, a struggling student, a small business about to fail."),
        B("c9_04", "And then comes a hard decision, with three paths that all seem logical."),
        B("c9_05", "Path one: use your mind for status and control."),
        B("c9_06", "Path two: chase knowledge alone, never asking who your discoveries might affect."),
        B("c9_07", "Path three: use it to make life better, for yourself and for others."),
        B("c9_08", "You run every calculation you can. But every path has trade-offs, and no equation can tell you what you truly value.", gap=1.3),
        B("c9_09", "Intelligence is a tool. It doesn't decide your character. You do."),
        B("c9_09b", "The same brilliant mind could build a hospital or a weapon. The choice is yours."),
        B("c9_10", "So you choose a project that matters... and make time for the people who matter, too.", gap=1.3),
        B("c9_11", "And one evening, on a hill above the city lights, you wonder what really makes a life worthwhile.", gap=1.5),
    ],
    10: [
        B("c10_01", "So, what would happen if you had an IQ of 500?"),
        B("c10_02", "In this thought experiment, you might learn at an extraordinary rate, recognize patterns others miss, and imagine solutions to problems that seem impossible today."),
        B("c10_03", "But you wouldn't automatically know everything."),
        B("c10_04", "You wouldn't become immune to mistakes."),
        B("c10_05", "And you wouldn't suddenly understand what makes every person happy, what the future holds, or what you should do with your life."),
        B("c10_06", "Because intelligence can help you answer questions.", gap=1.3),
        B("c10_07", "It can help you discover how the world works."),
        B("c10_08", "It can even help you change the future."),
        B("c10_09", "But knowing what is possible is not the same as knowing what is worth doing.", gap=1.5),
        B("c10_10", "Maybe the most important question isn't how intelligent you could become.", gap=1.3),
        B("c10_11", "Maybe it's what you would choose to do with the intelligence you already have."),
        B("c10_12", "Because even in a world where you could solve almost any puzzle, one question might remain:", gap=1.3),
        B("c10_13", "What kind of person would you choose to be?", gap=1.5),
    ],
}


def all_beats():
    for ch in sorted(BEATS):
        for b in BEATS[ch]:
            yield ch, b


if __name__ == "__main__":
    total = 0
    for ch in sorted(BEATS):
        n = sum(len(b["text"].split()) for b in BEATS[ch])
        total += n
        print(f"chapter {ch:2d}: {n:4d} words")
    print("total:", total)
