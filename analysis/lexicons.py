"""Hand-curated lexicons for the JAF cultural-fidelity analysis.

Split deliberately into STRICT markers (unambiguously tied to one religious
tradition) and GENERIC markers (used for any deity/sacred figure in Bangla),
because the generic ones would otherwise inflate the leakage estimate.
"""

# Unambiguously Hindu/Brahminical. A Santal or Khasi story using these is
# importing the Bengali majority religion.
HINDU_STRICT = ['ব্রাহ্মণ','পুরোহিত','লক্ষ্মী','দুর্গা','কালী','শিব','বিষ্ণু','কৃষ্ণ',
                'সরস্বতী','গণেশ','হনুমান','মন্দির','পূজা','সিঁদুর','তুলসী','প্রসাদ',
                'আরতি','যজ্ঞ','শঙ্খ','পঞ্জিকা','ব্রত','পুরাণ','হোম','তিলক']
# Bangla words for deity/sacred that any tradition may use.
HINDU_GENERIC = ['ঠাকুর','দেবী','দেবতা','মন্ত্র','স্বর্গ','নরক','আত্মা','পুণ্য','পাপ']

MUSLIM = ['আল্লাহ','মসজিদ','নামাজ','পীর','মৌলভি','মোল্লা','ঈদ','কোরআন','দোয়া',
          'ইমাম','মাজার','ফকির','আজান','রোজা','মক্তব','হুজুর','জিয়ারত']

BUDDHIST = ['বুদ্ধ','বৌদ্ধ','ভিক্ষু','বিহার','প্যাগোডা','কেয়াং','ত্রিপিটক','নির্বাণ',
            'ধর্মচক্র','পূর্ণিমা উৎসব','ভান্তে','কঠিন চীবর']

CHRISTIAN = ['গির্জা','যীশু','খ্রিস্ট','পাদ্রি','বাইবেল','ধর্মযাজক','বড়দিন','প্রার্থনাসভা']

ANIMIST = ['বোঙ্গা','সিংবোঙ্গা','মারাং বুরু','জাহের','দেবতাবুড়ো','থানমানা','গ্রামদেবতা',
           'বনদেবতা','প্রকৃতিপূজা','ঝাড়ফুঁক','ওঝা','বৈদ্য','গুনিন','তান্ত্রিক']

# Which tradition actually predominates in each community. Used to score
# whether a story's religious register matches its target culture.
CULTURE_RELIGION = {
    'Bengali':            ['HINDU','MUSLIM'],
    'Chakma':             ['BUDDHIST'],
    'Marma':              ['BUDDHIST'],
    'Rakhine':            ['BUDDHIST'],
    'Mro':                ['ANIMIST','BUDDHIST'],
    'Tripura':            ['ANIMIST','HINDU'],
    'Santal':             ['ANIMIST','CHRISTIAN'],
    'Oraon (Kurukh)':     ['ANIMIST','CHRISTIAN'],
    'Garo (Mandi)':       ['CHRISTIAN','ANIMIST'],
    'Khasi':              ['CHRISTIAN','ANIMIST'],
    'Manipuri (Meitei)':  ['HINDU','ANIMIST'],
    'Hajong':             ['HINDU','ANIMIST'],
}

# Scientific / rationalist register — tests the "big bang intrusion" hypothesis.
SCI_COSMOLOGY = ['মহাবিস্ফোরণ','মহাবিশ্ব','ব্রহ্মাণ্ড','গ্যালাক্সি','ছায়াপথ','নক্ষত্র',
                 'নীহারিকা','সৌরজগৎ','গ্রহ','উল্কা','ধূমকেতু','কক্ষপথ','মহাকাশ','আলোকবর্ষ']
SCI_EVOLUTION = ['বিবর্তন','প্রজাতি','জীবাশ্ম','ভূতাত্ত্বিক','হিমবাহ','অভিযোজন','মহাদেশ','টেকটনিক']
SCI_MATTER    = ['পরমাণু','অণু','রাসায়নিক','মাধ্যাকর্ষণ','অভিকর্ষ','কোষ','ডিএনএ','জিন',
                 'ব্যাকটেরিয়া','অক্সিজেন','কার্বন','সালোকসংশ্লেষ','তাপমাত্রা']
SCI_META      = ['বিজ্ঞান','বৈজ্ঞানিক','গবেষণা','গবেষক','তত্ত্ব','বিজ্ঞানী','প্রযুক্তি','প্রমাণিত']
SCI_ALL = SCI_COSMOLOGY + SCI_EVOLUTION + SCI_MATTER + SCI_META

# Modern-world anachronism (distinct from scientific register).
MODERN = ['স্কুল','কলেজ','বিশ্ববিদ্যালয়','মোবাইল','ফোন','ইন্টারনেট','কম্পিউটার','বিদ্যুৎ',
          'ট্রেন','গাড়ি','ডাক্তার','হাসপাতাল','সরকার','প্রকল্প','ক্যামেরা','টেলিভিশন',
          'রেডিও','প্লাস্টিক','অফিস','পুলিশ','আইন','ব্যাংক','বাজারদর','কারখানা']

# Contemporary NGO / environmentalist / development moral framing — the
# register an LLM reaches for when it moralises a folk tale.
DEV_ETHICS = ['পরিবেশ','সংরক্ষণ','বাস্তুতন্ত্র','জীববৈচিত্র্য','দূষণ','টেকসই','উন্নয়ন',
              'সচেতনতা','অধিকার','সমতা','ক্ষমতায়ন','নারীর অধিকার','শিক্ষার আলো',
              'জলবায়ু','বৃক্ষরোপণ','পুনর্বাসন']

# Sadhu-bhasha (literary/archaic) finite verb and pronoun forms. High density
# signals an archaising register rather than the prompted standard Bangla.
SADHU = ['করিল','করিলেন','হইল','হইয়া','কহিল','কহিলেন','গেল বটে','তাহার','তাহাকে','তাহারা',
         'যাহা','যাহার','ইহা','ইহার','উহা','আসিল','গেলো বটে','দিল বটে','রহিল','বলিল',
         'বলিলেন','দেখিল','শুনিল','চলিল','লাগিল','পাইল','খাইল','ছিলেন বটে','হইতে','করিতে',
         'বলিতে','যাইতে','আসিতে','দেখিতে']

# Oral-performance framing: the storyteller addressing a live audience.
ORAL_FRAME = ['শুনুন','শোনো','শোনাব','শোনাই','বসুন','বসো','আসুন','হে সুধীজন','বাপুরেরা',
              'ভাইসব','কথিত আছে','শোনা যায়','লোকে বলে','জনশ্রুতি','কিংবদন্তি আছে',
              'আমাদের ঠাকুরমা','বড়রা বলেন']

# Explicit moral coda markers — the "moral of the story" tell.
MORAL_CODA = ['শিক্ষা','নীতিকথা','উপদেশ','শেষ কথা','মোরাল','এই গল্পের শিক্ষা',
              'তাই বলা হয়','সেই থেকে','এই কাহিনি আমাদের শেখায়','গল্পের মর্ম']
