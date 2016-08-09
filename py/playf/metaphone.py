# coding=utf-8
__author__ = 'PV-Kara'

def metaphone( word ):
    invalidChars = u'ъь'                            # алфавит исключаемых букв
    voicedConsonants = u'бздвг'			            # звонкие согласные
    surdConsonants = u'пстфк' 			            # глухие согласные
    consonants = u'псткбвгджзфхцчшщ'		        # согласные, перед которыми звонкие оглушаются
    vowels1 = u'оюеэяёы'				            # образец и замена гласных
    vowels2 = u'ауииаиа'
    result = [];


    for ch in word:                                 # убираем символы учитывая validChars
        if ch not in invalidChars:
            result.append(ch);

    c1 = 0;
    for i in xrange(len(result)-1,-1,-1):       # вот так в питоне уродево сделано итерация с хвоста массиво (((
        c2 = result[i]
        # убираем дублирование перед заменой
        if c1 == c2:
            del result[i];
            continue;
        # заменяем гласные
        if vowels1.count(c2):
            c2 = vowels2[vowels1.index(c2)];
            result[i] = c2;
        # оглушение согласных
        if (c1 == 0 or consonants.count(c1)) and voicedConsonants.count(c2):
            c2 = surdConsonants[voicedConsonants.index(c2)];
            result[i] = c2;

        if c1 == consonants[1] and c2 == consonants[2]:
            del result[i];
            result[i] = consonants[12];
        # убираем дублирование после замены
        if c2 == c1:
            del result[i];
        else:
            c1 = c2;
        
    return ''.join(result);

print metaphone(u'Аввакумовъ'.lower())
print metaphone(u'Авакумовь'.lower())
print metaphone(u'потсышеватс'.lower())
print str('к' == 'к')



  