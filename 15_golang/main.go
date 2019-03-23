package main

import (
	"appinstalled"
	"compress/gzip"
	"encoding/csv"
	"flag"
	"fmt"
	"github.com/bradfitz/gomemcache/memcache"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
)

type AppInstalled struct {
	dev_type string
	dev_id   string
	lat      float64
	lon      float64
	apps     []uint32
}

type ResultError struct {
	app AppInstalled
	err error
}

type ExecutionResult struct {
	processed int
	errors    int
}

var normalErrorRate float64 = 0.01

func main() {
	var wg sync.WaitGroup

	result := &ExecutionResult{processed: 0, errors: 0}
	cli := parseCliArgs()
	files, err := filepath.Glob(cli["pattern"])
	if err != nil {
		log.Printf("Could not find files for the given pattern: %s", cli["pattern"])
		return
	}
	fileReader := make(chan []string)   // Read file
	appParser := make(chan ResultError) // Make app_installed instance for file's lines
	memcacheWriter := make(chan string) // Write to memcache

	wg.Add(3)
	go func() {
		defer wg.Done()
		for _, f := range files {
			processFile(f, fileReader)
			dotRename(f)
		}
		close(fileReader)
	}()

	go func(result *ExecutionResult) {
		defer wg.Done()
		for content := range fileReader {
			for _, line := range content {
				result.processed++
				parseAppsinstalled(line, appParser)
			}
		}
		close(appParser)
	}(result)

	go func(result *ExecutionResult) {
		defer wg.Done()
		for app := range appParser {
			if app.err == nil {
				saveToMemCache(&app.app, cli, memcacheWriter)
			} else {
				result.errors++
			}
		}
		close(memcacheWriter)
	}(result)

	for mw := range memcacheWriter {
		log.Print("Saved to memcache", mw)
	}

	wg.Wait()

	errs_rate := 0.0
	if result.processed == 0 {
		errs_rate = 1
	} else {
		errs_rate = float64(result.errors) / float64(result.processed)
	}

	if errs_rate < normalErrorRate {
		log.Print("Acceptable error rate")
	} else {
		log.Fatal("High error rate")
	}
}

func saveToMemCache(app *AppInstalled, cli map[string]string, w chan string) {
	device_memc := map[string]string{
		"idfa": cli["idfa"],
		"gaid": cli["gaid"],
		"adid": cli["adid"],
		"dvid": cli["dvid"],
	}
	memc_addr := device_memc[app.dev_type]
	ua := appsinstalled.UserApps{
		Apps: app.apps,
		Lat:  &app.lat,
		Lon:  &app.lon,
	}
	key := app.dev_type + "%" + app.dev_id
	packed := ua.String()
	client := memcache.New(memc_addr)
	client.Set(&memcache.Item{Key: key, Value: []byte(packed)})

	w <- packed
}

func parseCliArgs() map[string]string {
	testFlag := flag.String("test", "false", "store_true")
	logFlag := flag.String("log", "false", "store")
	dryFlag := flag.String("dry", "false", "store")

	patternFlag := flag.String("pattern", "/data/appsinstalled/*.tsv.gz", "pattern flag")
	idfaFlag := flag.String("idfa", "127.0.0.1:33013", "Flag for idfa config")
	gaidFlag := flag.String("gaid", "127.0.0.1:33014", "Flag for gaid config")
	adidFlag := flag.String("adid", "127.0.0.1:33015", "Flag for adid config")
	dvidFlag := flag.String("dvid", "127.0.0.1:33016", "Flag for dvid config")

	flag.Parse()

	return map[string]string{
		"test":    *testFlag,
		"log":     *logFlag,
		"dry":     *dryFlag,
		"pattern": *patternFlag,
		"idfa":    *idfaFlag,
		"gaid":    *gaidFlag,
		"adid":    *adidFlag,
		"dvid":    *dvidFlag,
	}
}

func parseAppsinstalled(line string, p chan ResultError) {
	line_parts := strings.Split(line, "\t")
	if len(line_parts) < 5 {
		p <- ResultError{app: AppInstalled{}, err: fmt.Errorf("Length is less than 5")}
		return
	}

	dev_type := line_parts[0]
	dev_id := line_parts[1]
	lat := line_parts[2]
	lon := line_parts[3]
	raw_apps := line_parts[4]
	if dev_type == "" || dev_id == "" {
		p <- ResultError{app: AppInstalled{}, err: fmt.Errorf("dev type or dev id do not present")}
		return
	}
	raw_apps_splitted := strings.Split(raw_apps, "\t")
	var raw_apps_uint []uint32
	for _, v := range raw_apps_splitted {
		app_id, _ := strconv.ParseInt(v, 10, 32)
		raw_apps_uint = append(raw_apps_uint, uint32(app_id))
	}
	lat_float, lat_err := strconv.ParseFloat(lat, 64)
	lon_float, lon_err := strconv.ParseFloat(lon, 64)
	if lat_err != nil || lon_err != nil {
		p <- ResultError{app: AppInstalled{}, err: fmt.Errorf("Invalid geo cords")}
		return
	}
	app := AppInstalled{
		dev_type: dev_type,
		dev_id:   dev_id,
		lat:      lat_float,
		lon:      lon_float,
		apps:     raw_apps_uint,
	}
	p <- ResultError{app: app, err: nil}
}

func processFile(file string, c chan []string) {
	content := getFileContent(file)
	c <- content
}

func getFileContent(file string) []string {
	f, err := os.Open(file)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	gr, err := gzip.NewReader(f)
	if err != nil {
		log.Fatal(err)
	}
	defer gr.Close()

	cr := csv.NewReader(gr)
	rec, err := cr.Read()
	if err != nil {
		log.Fatal(err)
	}
	return rec
}

func dotRename(filename string) {
	newName := "." + filename
	os.Rename(filename, newName)
}
