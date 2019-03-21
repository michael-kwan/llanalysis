from process_data import read_dataset, get_player_stats


if __name__ == "__main__":
    names = read_dataset('../data', '80players.txt')
    ff_rates = []
    counter = 0
    sumcount = 0
    f = open('output.txt', 'w')
    for name in names:
        counter += 1
        ffr, success = get_player_stats(name)
        ff_rates.append(ffr)
        sumcount += success
        print ("FF rate for " + name + ": " + str(ffr) + " percentile: " + str(sumcount/counter) + "\n")
        f.write("FF rate for " + name + ": " + str(ffr) + " percentile: " + str(sumcount/counter) + "\n")
        if counter % 100 == 0:
            print (counter)
        