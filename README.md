COMS E6111 Advanced Database Systems (Columbia Computer Science, Prof. Luis Gravano)

Spring 2014 Project 1

Relevance Feedback & Query Expansion

(assignment: http://www.columbia.edu/~sy2515/COMS_E6111_Project_1.pdf)


a.  Team members:

    Yunao Liu - yl3055

    Shuo Yang - sy2515


b.  List:

    README

    Makefile

    Main.py

    Interface.py

    Core.py

    Rocchio.py

    Vectorization.py

    RSVScoring.py

    Clear.py

    stemming

    transcript_columbia

    transcript_gates

    transcript_snow_leopard


c.  How to run:
./Makefile 

After running this bash script, you are supposed to enter the initial query terms and the target precision first:

>Please input query

>gates

>Please input target precision

>0.9

Then a total of 10 query results given by Bing will show out one by one, with "Title", "Summary" and "URL". You are at the same time asked whether this result is relevant or not. You are supposed to input "y/Y" or "n/N" according to your personal judgement about the relevance of this exact query result. You should make a clear and unbiased judgement otherwise there will be something confusing in the following query round, and you will even hardly get what you want from Bing.

>Title:    Gates Corporation

>Summary:  Gates Corporation is Powering Progress™ in the Oil & Gas, Energy, Mining, Marine, Agriculture, Transportation and Automotive Industries.

>URL:      gates.com

>Is this result relevant or not? Please input Y/N

>n

>...


d.  Internal design:

Our project can be majorly divided into two parts: supporting part and core part.
 
The job of supporting part is to maintain the running logic of the whole project, including receiving user input query, interacting with Bing API, parsing HTML file, analyzing user judgments and processing text into separately words.
 
At the beginning of program, the supporting part will first get initial user query and target precision. Then it will request search result from Bing API. After getting search results, user will give judgment of each result, and supporting part will process result title, summary and other information get from HTML file, and give them to core part along with user’s judgment. After core part return new query, the supporting part will begin the loop again till target precision is met.
 
The job of core part will be discussed in detail in the next part. 


e.  Query-modification method:

Here is the structure of our whole project, with detailed descriptions in each of the modules:

->Interface:
It's a self-defined class, used to store the query result returned by Bing, and transferred from Main module to Core module, which will be discussed below. It stores the BOW (bag of word) information for the title, summary and text information of each query result. URL of this query result is also stored in it; and relevance of this query result is stored as a bool variable.

->Main:
It's the user-interface design. It sends user’s inputs to Bing search engine, and get the query results from Bing. It also pre-processes the query results (removing punctuation, removing stop words, stemming, getting text information using the URL of the query result - crawling). After all of these, 10 query results will be given to the Core module, for further processing (query expansion).

->Core:
It's just an interface module between the Main module and the algorithm parts. As we two team members separately develop this two parts, we use this Core module as a programming interface. In this module, we can try different models and set different algorithm parameters to do some experiments, and try to get the optimal parameters for each algorithm.

->Rocchio:
The main scripts of Rocchio algorithm's implementation. Actually we make many parameters variable. For example, we can change the alpha, beta and gamma parameters in the standard Rocchio algorithm manually when this module is called; and we can choose to add one or two new query terms in each round; and we can choose to use standard Rocchio, original query vector adding positive-feedback only Rocchio, and original query vector adding positive-feedback and the most dominant negative-feedback Rocchio; and we can choose to use different BOW space, such as title only, summary only, text only, and any two of them combination, and three of them combination. The reason we make all of these circumstances possible to operate is that we want to test different parameters and algorithm models to get the best one for this exact job. And after several experiments, we use the standard Rocchio with parameters as (alpha=1, beta=0.75 and gamma=0.15), and we decide to add exact one new query term in each round, and we use the combination of title and summary information as the BOW space because we find that text information will bring more noise. We use this Rocchio algorithm to get the term in the vector space with the biggest weight and send it back to the new query round. This selection of model and parameters are based on the given testing cases. So we can't guarantee they can perform as better as we did when you test other unseen cases in the future. The Rocchio will need some information of each document such as TF of each word. They are given by the next module - Vectorization.

->Vectorization:
We call this module as Vectorization other than Inverted-index building in which the position information of a term is always preserved, because we don't build the inverted index actually. As we want to try some algorithm which don't use the position information of each term, so we just simply drop the position information, and only give back the term-frequency vector for each document by this Module. When we tested the algorithm, we found that we should care about the position of each of the query term. Maybe simply dropping the position information is not appropriate, and we should use them to sort the new query terms. For example, when we test the “columbia”, if we only use the weight of updated query vector from Rocchio to choose the new query terms and decide their positions, the second round we will use “university columbia”. But this order will not efficiently get a precision@10 as 0.9, which means that we need another query round. We manually set the order of this two terms as “columbia university” in this round, then we can get a precision@10 as 0.9 just in this round other than another more round. If I have time in the future, I will try it. You can refer to the additional information for this sorting algorithm. If I can finish this algorithm before the deadline, I will show it in that part. Actually, we also tried another algorithm called RSVScoring algorithm, which will be further discussed below. And this algorithm also need the term-frequency vector from this Vectorization module.

->RSVScoring:
Reference Paper:
Examining and improving the effectiveness of relevance feedback for retrieval of scanned text documents, Adenike M. Lam-Adesina, Gareth J.F. Jones, June 2005
detailed RSV calculation formula:

	The formula is :

	TF   : term frequency, actually no help in our global environment

	DF   : document frequency

	DFR  : document frequency in relevant documents

	num  : total number of documents

	numR : number of relevant documents

	RW(word) = log( ( (DFR + 0.5) * (num - DF - numR + DFR + 0.5) )

			/ ( (DF - DFR + 0.5) * (numR - DFR + 0.5) ) )

	RSV(word) = RW(word) * DFR

	Then we choose the word (or words) who has the highest RSV to be the next query keyword.
No more words about this algorithm. We just tested it but finally decided to use the Rocchio algorithm in the program other than this one, because we find that for the given cases, the Rocchio performs better.

->Clear:
It's just for fun. As we use the Google Docs as the code repository other than some stardard version control systems such as GitHub, when we run the program, some intermediate files will be generated and left in the Google Docs. We want to keep the folder clean after each execution of our program. So we write this to remove all the *.pyc and *.swp files.

The above are all the ideas and implementations of our project. I think I can briefly conclude what we do: we use the Bing API as others did; we try crawling the text, different Rocchio models, different parameters in Rocchio model, and another model - RSVScoring, and we finally choose the seemingly best model with most optimal parameters, at least for the given test cases. We know that such project is not about finishing something. It actually is about trying, experimenting and optimizing, and these are exactly what we did in this project.


f.  Bing search key:
    ********************************************


g.  Additional information:

I have finished the bi-gram detection algorithm. The reason why I want to use this bi-gram detection algorithm is that, I find sometimes there exists bi-gram which will greatly improve the query precision if the words in it are in the correct order. As described above, when we query the “columbia”, we find that if we only use the Rocchio weight to decide the terms’ positions, then the second round query should be “university columbia”. By manually testing we find that if the new query is “columbia university” in that round, then we only need 2 rounds to achieve precision@10 of 0.9, other than 3 rounds when “university columbia” is used. So we feel that it is necessary to detect such kind of bi-gram.

But the problem is, how many bi-gram should we use? Let’s think of our algorithm. By experiments we find that it is more appropriate to add exact one new query word to the query, leading to a sound, slowly and safely query expansion. We always choose the term with the highest Rocchio vector weight as the new term. In this scenario, we feel that it is with very low possibility that we can find many bi-grams in the query terms. Also, the bi-gram algorithm is only a supplementary to the main Rocchio expansion method (for example, for the “snow leopard”, we can only get the exact query precision by adding another key word about “Apple Mac OS X” or something like that, otherwise the simple bi-gram of “snow leopard” will lead us to unexpactation). We hope to find that bi-gram and wish it can perform better in the new query. But we should at the same time have limited expectation. If we can find a bi-gram, it’s good, and under most circumstances it can always improve the new query result. But if we can’t find one, it’s also no problem. With such an attitude, we decide to only find one most frequent bi-gram among all the bi-grams in the query term. But again, why we use bi-gram, other than 3-gram or gram with more words in it? It’s also due to our limited expectation. You know, there is very little probability that a 3-gram can exist and exactly express what we want to query from search engine. Another thing is that if this 3-gram actually exists, we can also get a bi-gram from it which can also play an important role in talking about what we are thinking. So, we choose to use bi-gram detection.

Now is the detailed algorithm. Again, we still don’t build the inverted-index, because we only need to detect the bi-gram in the BOW. We get every title and summary BOW list first, and in each of these lists we detect all the 2-permutations of the query terms to find the bi-gram and its total frequency. At last we pick up the bi-gram with the highest frequency as the target, if there exists any bi-gram in the BOW space. After this, we look back to the Rocchio vector weight to sort this bi-gram and the left terms. We use the average of this two words in the bi-gram as its score, and for others we just use their weight. Here we have a strange phenomenon in the process. As the previous query terms will always appear in the query results of this round, due to the weight calculation method (actually due to document frequency - larger number leads to a smaller weight), their Rocchio vector weight always have a smaller value. So actually the new added query word always lies ahead. But it’s no problem. If we can find a bi-gram, it is really helpful for us to quickly terminate the query process.

I think there are still improvement space for our bi-gram detection. For example, we should set a threshold for the frequency of bi-gram. If two non-bi-gram words accidentally meet each other (one at the end of one sentence and another at the beginning of the next setence, and because we have removed the punctuation so they may meet each other accidentally), and we still regard them as a bi-gram, this will bring bad effect for our new query, because we actually strengthen the relationship of this two words and we may get an unexpected query result, maybe. So a threshold should be used for this.
