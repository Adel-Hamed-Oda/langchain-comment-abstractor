import OpenAIAgent
import csv

API_KEY = "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"

def main():
    with open('data.csv', mode='r', newline='') as file:
        reader = list(csv.DictReader(file))
        headers = reader[0].keys() if reader else []

    comments = str([row.get("comment", "").strip() for row in reader])
    comments.replace(",,", ",no comment,")

    try:
        model = OpenAIAgent.Model(key = API_KEY)
    except ValueError:
        print("please provide a valid API key, use: key = '...'")
        return

    system_msg = str(
        "You will receive a list of strings corresponding to comments. " +
        "Your task is to convert each comment into a short abstraction (1-5 words). " +
        "Return the same number of items, maintaining order. " +
        "Do not add extra text or change the format." +
        "Please don't mess this up"
    )

    model.send(system_msg, "system")
    model.send(comments, "human")
    model.process()
    result = model.receive()
    model.clear()
    
    system_msg = str(
        "You will receive a list of strings corresponding to some abstractions about some comments. " +
        "You will also receive a list containing all the comments themselves. " +
        "Your job is to look at each comment in the 2nd list, and replace it with the appropriate abstraction from the first list. " +
        "make sure you try doing this for every comment and that the result is the same length as the original list of comments. " +
        "Do not add extra text or change the format." +
        "Please don't mess this up"
    )

    model.send(system_msg, "system")
    model.send(result, "human")
    model.send(comments, "human")
    model.process()

    result = read_result_into_list(model.receive())

    if len(result) != len(reader):
        print("=== result === " + str(result))
        print("=== result length === " + str(len(result)))
        print("=== original length === " + str(len(reader)))
        print("=== comments === " + comments)
        return

    for i, row in enumerate(reader):
        row["comment"] = result[i].strip().replace('[', '').replace(']', '').replace("'", "")

    with open('data.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(reader)

    model.clear()

    print("Process done with success")

def read_result_into_list(result):
    if isinstance(result, list):
        return [item.strip() for item in result]
    elif isinstance(result, str):
        return [item.strip() for item in result.split(",")]
    else:
        raise TypeError("Please make sure the results are in a valid format")

if __name__ == "__main__":
    main()