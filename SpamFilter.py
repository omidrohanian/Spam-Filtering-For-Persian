import collections, os

def words(filename):
    with open(filename,'r', encoding='utf-8') as infile:
        return [word.strip().lower() for line in infile for word in line.split()]

def lexicon(k = 5):
    # Extract training directories
    spam_training_directory = os.getcwd() + '/emails/spamtraining'
    ham_training_directory  = os.getcwd() + '/emails/hamtraining'

    # Create spam distribution
    spam_distribution = collections.defaultdict(lambda: 1)
    files = os.listdir(spam_training_directory)
    
    for f_name in files:
        list_of_words = words(spam_training_directory + '/' + f_name)
        for word in list_of_words:
                spam_distribution[word] += 1

    ham_distribution = collections.defaultdict(lambda: 1)
    files = os.listdir(ham_training_directory)
    for f_name in files:
        list_of_words = words(ham_training_directory + '/' + f_name)
        for word in list_of_words:
                ham_distribution[word] += 1

    # Remove all key,value pairs that have a value less than k
    hamkeys  = ham_distribution.keys()
    spamkeys = spam_distribution.keys()
    for key in spamkeys:
        if spam_distribution[key] < k:
            del spam_distribution[key]

    for key in hamkeys:
        if ham_distribution[key] < k:
            del ham_distribution[key]

    return ham_distribution, spam_distribution

def probability(word, ham_distribution, spam_distribution):
    # NS = the number of times w appeared in spam
    # TS = total number of words in spam
    # NH = the number of times w appeared in ham
    # TH = total number of words in spam
    # P(S | w) = (NS/TS) / ((NS/TS) + (2 * NH))

    spam_keys = spam_distribution.keys()
    ham_keys = ham_distribution.keys()
    num_of_hams = sum(ham_distribution.values())
    num_of_spams = sum(spam_distribution.values())
    if (word in spam_keys) and (word not in ham_keys) and (spam_distribution[word]>10):
        return 0.9999
    elif (word in ham_keys) and (word not in spam_keys):
        return 0.0001
    elif word not in (spam_keys or ham_keys):
        return 0.4
    else: 
        numerator = spam_distribution[word]/num_of_spams
        denominator = numerator + ((2 * ham_distribution[word])/num_of_hams) 
        return numerator / float(denominator)

def classify_email(email, ham_distribution, spam_distribution):
    email_words = words(email)
    appeal = {}
    for word in email_words:
        appeal[word] = abs(probability(word, ham_distribution, spam_distribution) - 0.5)
    appeal_list = sorted(appeal, key=appeal.get, reverse=True)
    spam_probability = 1
    ham_probability = 1
    # P_i = P(S|w_i)
    # P(H|w_i) = P(S|w_i) = 1 - P_i
    # P(S|E) = (Π P_i)/((Π P_i)+(Π 1-P_i))
    for word in appeal_list[:15]:
        p = probability(word, ham_distribution, spam_distribution)
        spam_probability *= p
        ham_probability *= (1-p)
    total = spam_probability/(spam_probability+ham_probability)

    if total > 0.99999:
        return 'spam'
    else:
        return 'ham'

def test_filter(hamtesting, spamtesting, k = 5):
    ham_distribution, spam_distribution = lexicon()

    spam_as_ham = []
    ham_as_spam = []

    ham_hit   = 0
    ham_total = 0
    ham_testing_files = os.listdir(hamtesting)
    for file in ham_testing_files:
        if classify_email(hamtesting + '/' + file, ham_distribution, spam_distribution) == 'ham':
                ham_hit += 1
        else:
            ham_as_spam.append(file)
        ham_total += 1

    spam_hit   = 0
    spam_total = 0
    spam_testing_files = os.listdir(spamtesting)
    for f_name in spam_testing_files:
        if classify_email(spamtesting + '/' + f_name, ham_distribution, spam_distribution) == 'spam':
            spam_hit += 1
        else:
            spam_as_ham.append(f_name)
        spam_total += 1

    ham_hit_ratio  = ham_hit / float(ham_total)
    spam_hit_ratio = spam_hit / float(spam_total)

    return ham_hit_ratio, spam_hit_ratio, ham_total, spam_total, ham_as_spam, spam_as_ham


spamtesting = os.getcwd() + '/emails/spamtesting'
hamtesting  = os.getcwd() + '/emails/hamtesting'

ham_hit_ratio, spam_hit_ratio, ham_total, spam_total, ham_as_spam, spam_as_ham = test_filter(hamtesting, spamtesting)

print() 
print ("Correct Ham Percentage:     ", ham_hit_ratio * 100)
print ("Correct Spam Percentage:    ", spam_hit_ratio * 100)
print ("Correct Overall Percentage: ", ((ham_hit_ratio*ham_total + spam_hit_ratio*spam_total) / (ham_total + spam_total)) * 100)

print ("\nHam Incorrectly Labelled as Spam:")
for file in ham_as_spam:
	print ("\t"+file)

print ("\nSpam Incorrectly Labelled as Ham:")
for file in spam_as_ham:
	print ("\t"+file)
print()
