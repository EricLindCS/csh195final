var curatorMode = false;

var apiUrl2 = '127.0.0.1:5000';
var apiUrl1 = 'api.tosdr.org';


function new_populateList(points: any) {

    const pointsList = document.getElementById('pointList');

    // Convert array of arrays to array of objects
    points = points.map((point: any) => ({
        title: point[0],
        classification: point[1]
    }));

    const blockerPoints = points.filter(
        (point: any) => point.classification === 'blocker'
    );
    const badPoints = points.filter(
        (point: any) => point.classification === 'bad'
    );
    const goodPoints = points.filter(
        (point: any) => point.classification === 'good'
    );
    const neutralPoints = points.filter(
        (point: any) => point.classification === 'neutral'
    );

    new_createPointList(blockerPoints, pointsList, false);
    new_createPointList(badPoints, pointsList, false);
    new_createPointList(goodPoints, pointsList, false);
    new_createPointList(neutralPoints, pointsList, true);
}

function new_createPointList(pointsFiltered: any, pointsList: any, last: boolean) {

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "ADDING" });
    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: pointsFiltered });


    var added = 0;
    for (let i = 0; i < pointsFiltered.length; i++) {
        const point = document.createElement('div');
        var temp = `
        <div class="point ${pointsFiltered[i].classification}">
            <img src="icons/${pointsFiltered[i].classification}.svg">
            <p>${pointsFiltered[i].title}</p>
        </div>`;
        point.innerHTML = temp.trim();
        pointsList.appendChild(point.firstChild);
        added++;
        if (i !== pointsFiltered.length - 1) {
            const divider = document.createElement('hr');
            pointsList.appendChild(divider);
        }
    }
    if (added !== 0 && !last) {
        const divider = document.createElement('hr');
        divider.classList.add('group');
        pointsList.appendChild(divider);
    }
}

async function new_getServiceDetails(id: string, unverified = false) {

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "ATTEMPTING SUMMARY" });

    const service_url = `http://${apiUrl2}/fetch?url=https://${id}/`;

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: service_url });

    const response = await fetch(service_url);

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "Fetched" });

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: response });

    // check if we got a 200 response
    if (response.status >= 300) {
        chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "SYMMARY FAILED 300" });

        document.getElementById('loading')!.style.display = 'none';
        document.getElementById('loaded')!.style.display = 'none';
        document.getElementById('error')!.style.display = 'flex';
        return;
    }

    const data = await response.json();

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "SUMMARYDATA" });
    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: data });
    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: data.error });

    const name = "AI Generated Summary"//data.parameters.name;
    const rating = '' //data.parameters.rating;
    const points = data.privacy_analysis;

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: points.length });


    const serviceNames = document.getElementsByClassName('serviceName');

    for (let i = 0; i < serviceNames.length; i++) {
        (serviceNames[i] as HTMLElement).innerText = name;
    }

    document.getElementById('title')!.innerText = name;
    const logo = document.getElementById('logo') as HTMLImageElement;
        logo.src = `icons/icon128.png`;

    /*
    if (rating) {
        document
            .getElementById('gradelabel')!
            .classList.add(rating.toLowerCase());
        themeHeaderColorIfEnabled(rating.toLowerCase());
        document.getElementById('grade')!.innerText = rating;
    } else {
        document.getElementById('grade')!.innerText = 'N/A';
    }
    */
    document.getElementById('grade')!.innerText = 'N/A';


    document.getElementById('pointsCount')!.innerText = points.length;

    document.getElementById('loading')!.style.opacity = '0';
    document.getElementById('loaded')!.style.filter = 'none';
    setTimeout(function () {
        document.getElementById('loading')!.style.display = 'none';
    }, 200);

    if (unverified) {
        document.getElementById('isai')!.style.display = 'block';
    }

    document.getElementById('webbutton')!.style.display = 'none';

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "POPULATING"});
    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: points});

    new_populateList(points);
}

async function handleUrlInURLIfExists(urlOriginal: string) {
    var url = urlOriginal.split('?url=')[1];

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "ATT HDL URL"});


    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: url });
    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: urlOriginal });

    if (!url) {
        // no service-id in url, show error
        chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "!url"});

        document.getElementById('id')!.innerHTML = 'Error: no service-id in url';
        document.getElementById('loading')!.style.display = 'none';
        document.getElementById('loaded')!.style.display = 'none';
        document.getElementById('nourl')!.style.display = 'block';
        document.getElementById('pointList')!.style.display = 'none';
        return;
    }

    new_getServiceDetails(url,true);

    //removing search because lazy
    /*


    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "ATT SEARCH" });

    var result = await searchToSDR(url);

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: result });

    if (result) {

        chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "FOUND SEARCH" });


        document.getElementById('phoenixButton')!.onclick = function () {
            window.open(`https://edit.tosdr.org/services/${result}`);
        };

        themeHeaderIfEnabled(result);

        const logo = document.getElementById('logo') as HTMLImageElement;
        logo.src = `https://s3.tosdr.org/logos/${result}.png`;
        document.getElementById('id')!.innerText = result;

        getServiceDetails(result, true);

    } else {

        chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "NO FOUND SERARCH" });

        
        new_getServiceDetails(url,true);

        
        document.getElementById('id')!.innerText = 'Error: no service-id in url';
        document.getElementById('loading')!.style.display = 'none';
        document.getElementById('loaded')!.style.display = 'none';
        document.getElementById('nourl')!.style.display = 'block';
        document.getElementById('pointList')!.style.display = 'none';
        
    }
        */
}

function getServiceIDFromURL(url: string) {
    // get parameters from url
    var serviceID = url.split('?service-id=')[1];
    // whoops, no service-id in url, check if there's a url= parameter, maybe we just do not have it yet
    if (!serviceID) {
        chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "GOING TO URL HANDELER" });

        handleUrlInURLIfExists(url);
        return;
    }

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "GOT A SERVICE ID" });
    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: serviceID });



    // when you click on things in the popup, it appends a # to the url, so we need to remove that
    serviceID = serviceID.replace('#', '');

    if (serviceID === '-1') { // -1 is the default value for when the service is not found
        
        chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "Couldnotfind -1" });

        document.getElementById('id')!.innerHTML = 'Error: no service-id in url';
        document.getElementById('loading')!.style.display = 'none';
        document.getElementById('loaded')!.style.display = 'none';
        document.getElementById('nourl')!.style.display = 'block';
        document.getElementById('notreviewed')!.style.display = 'block';
        document.getElementById('pointList')!.style.display = 'none';
        document.getElementById('edittext')!.onclick = function () {
            window.open('https://edit.tosdr.org');
        };
        return;
    }

    document.getElementById('phoenixButton')!.onclick = function () {
        window.open(`https://edit.tosdr.org/services/${serviceID}`);
    };

    themeHeaderIfEnabled(serviceID);

    const logo = document.getElementById('logo') as HTMLImageElement;
    logo.src = `https://s3.tosdr.org/logos/${serviceID}.png`;
    document.getElementById('id')!.innerHTML = serviceID;

    getServiceDetails(serviceID);
}

function themeHeaderIfEnabled(serviceID: string) {
    chrome.storage.local.get(['themeHeader'], function (result) {
        if (result.themeHeader) {
            const blurredTemplate = `.header::before {
                content: '';
                position: absolute;
                background-image: url('https://s3.tosdr.org/logos/${serviceID}.png');
                top: 0;
                left: 0;
                width: 100%;
                height: 90%;
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
                filter: blur(30px);
                z-index: -2;
            }`;

            var styleElement = document.createElement('style');

            document.head.appendChild(styleElement);

            styleElement.sheet!.insertRule(blurredTemplate);
        }
    });
}

function themeHeaderColorIfEnabled(rating: string) {
    chrome.storage.local.get(['themeHeaderRating'], function (result) {
        if (result.themeHeaderRating) {
            const header = document.getElementById('headerPopup');
            header!.classList.add(rating);
        }
    });
}

async function getServiceDetails(id: string, unverified = false) {
    const service_url = `https://${apiUrl1}/service/v2/?id=${id}`;
    const response = await fetch(service_url);

    // check if we got a 200 response
    if (response.status >= 300) {
        chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "Couldnotfind >300" });

        document.getElementById('loading')!.style.display = 'none';
        document.getElementById('loaded')!.style.display = 'none';
        document.getElementById('error')!.style.display = 'flex';
        return;
    }

    const data = await response.json();

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: data });

    if (data.error !== 256) {
        chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "Couldnotfind !256" });

        document.getElementById('loading')!.style.display = 'none';
        document.getElementById('loaded')!.style.display = 'none';
        document.getElementById('error')!.style.display = 'flex';
        return;
    }

    const name = data.parameters.name;
    const rating = data.parameters.rating;
    const points = data.parameters.points;

    const serviceNames = document.getElementsByClassName('serviceName');

    for (let i = 0; i < serviceNames.length; i++) {
        (serviceNames[i] as HTMLElement).innerText = name;
    }

    document.getElementById('title')!.innerText = name;
    if (rating) {
        document
            .getElementById('gradelabel')!
            .classList.add(rating.toLowerCase());
        themeHeaderColorIfEnabled(rating.toLowerCase());
        document.getElementById('grade')!.innerText = rating;
    } else {
        document.getElementById('grade')!.innerText = 'N/A';
    }
    document.getElementById('pointsCount')!.innerText = points.length;

    document.getElementById('loading')!.style.opacity = '0';
    document.getElementById('loaded')!.style.filter = 'none';
    setTimeout(function () {
        document.getElementById('loading')!.style.display = 'none';
    }, 200);

    if (unverified) {
        document.getElementById('notreviewedShown')!.style.display = 'block';
    }

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: points });

    populateList(points);
}

function populateList(points: any) {
    const pointsList = document.getElementById('pointList');

    if (!curatorMode) {
        points = points.filter((point: any) => point.status === 'approved');
    } else {
        points = points.filter(
            (point: any) => point.status === 'approved' || point.status === 'pending'
        );
    }

    const blockerPoints = points.filter(
        (point: any) => point.case.classification === 'blocker'
    );
    const badPoints = points.filter(
        (point: any) => point.case.classification === 'bad'
    );
    const goodPoints = points.filter(
        (point: any) => point.case.classification === 'good'
    );
    const neutralPoints = points.filter(
        (point: any) => point.case.classification === 'neutral'
    );

    createPointList(blockerPoints, pointsList, false);
    createPointList(badPoints, pointsList, false);
    createPointList(goodPoints, pointsList, false);
    createPointList(neutralPoints, pointsList, true);
}

function curatorTag(pointStatus: string) {
    if (!curatorMode || pointStatus === 'approved') {
        return '';
    }
    return "<img src='icons/pending.svg'></img>";
}

function createPointList(pointsFiltered: any, pointsList: any, last: boolean) {
    var added = 0;
    for (let i = 0; i < pointsFiltered.length; i++) {
        const point = document.createElement('div');
        var temp = `
        <div class="point ${pointsFiltered[i].case.classification}">
            <img src="icons/${pointsFiltered[i].case.classification}.svg">
            <p>${pointsFiltered[i].title}</p>
            ${curatorTag(pointsFiltered[i].status)}
        </div>`;
        point.innerHTML = temp.trim();
        pointsList.appendChild(point.firstChild);
        added++;
        if (i !== pointsFiltered.length - 1) {
            const divider = document.createElement('hr');
            pointsList.appendChild(divider);
        }
    }
    if (added !== 0 && !last) {
        const divider = document.createElement('hr');
        divider.classList.add('group');
        pointsList.appendChild(divider);
    }
}

async function searchToSDR(term: string) {

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "STRT SEARCH" });


    const service_url = `https://${apiUrl1}/search/v4/?query=${term}`;
    const response = await fetch(service_url);

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: "SEARCH RESPONSE"});
    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: response });



    if (response.status !== 200) {
        document.getElementById('loading')!.style.display = 'none';
        document.getElementById('loaded')!.style.display = 'none';
        document.getElementById('error')!.style.display = 'flex';
        return;
    }

    const data = await response.json();

    chrome.runtime.sendMessage({ type: 'LOG_RESULT', result: data });

    if (data.error !== 256) {
        document.getElementById('loading')!.style.display = 'none';
        document.getElementById('loaded')!.style.display = 'none';
        document.getElementById('error')!.style.display = 'flex';
        return;
    }

    if (data.parameters.services.length !== 0) {
        const urls = data.parameters.service[0].urls as string[];
        for (let i = 0; i < urls.length; i++) {
            if (urls[i] === term) {
                return data.parameters.services[0].id;
            }
        }
    }
}

getServiceIDFromURL(window.location.href);

// Get settings
chrome.storage.local.get(['darkmode', 'curatorMode', 'api'], function (result) {
    if (result.darkmode) {
        const body = document.querySelector('body')!;

        body.classList.toggle('dark-mode');
    }

    if (result.curatorMode) {
        document.getElementById('curator')!.style.display = 'block';
        curatorMode = true;
    } else {
        document.getElementById('curator')!.style.display = 'none';
    }

    if (result.api) {
        if (result.api.length !== 0) apiUrl1 = result.api;
    }
});

// Event listeners

document.getElementById('toggleButton')!.onclick = function () {
    const body = document.querySelector('body')!;

    body.classList.toggle('dark-mode');

    const darkmode = body.classList.contains('dark-mode');

    chrome.storage.local.set({ darkmode: darkmode });
};

document.getElementById('settingsButton')!.onclick = function () {
    chrome.runtime.openOptionsPage();
};

document.getElementById('sourceButton')!.onclick = function () {
    window.open('https://github.com/tosdr/browser-extensions');
};


document.getElementById('source')!.onclick = function () {
    window.open('https://github.com/tosdr');
};

document.getElementById('opentosdr')!.onclick = function () {
    window.open('https://tosdr.org/');
};

// This is a hacky workaround for Firefox on desktop as it likes to resize the popup
// to the maximum width of the content, which is not what we want. Thanks, Mozilla.
function ifFirefoxDesktopResize() {
    // check useragent if firefox on desktop
    if (
        navigator.userAgent.includes('Firefox') &&
        !navigator.userAgent.includes('Mobile')
    ) {
        // resize window to stay at 350px
        document.body.style.width = '350px';
    }
}

ifFirefoxDesktopResize();
