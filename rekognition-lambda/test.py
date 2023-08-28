response = {
    'Labels': [
        {
            'Name': 'string1',
            'Confidence': '90',
            'Instances': [
                {
                    'BoundingBox': {
                        'Width': ...,
                        'Height': ...,
                        'Left': ...,
                        'Top': ...
                    },
                    'Confidence': ...,
                    'DominantColors': [
                        {
                            'Red': 123,
                            'Blue': 123,
                            'Green': 123,
                            'HexCode': 'string',
                            'CSSColor': 'string',
                            'SimplifiedColor': 'string',
                            'PixelPercent': ...
                        },
                    ]
                },
            ],
            'Parents': [
                {
                    'Name': 'string'
                },
            ],
            'Aliases': [
                {
                    'Name': 'string'
                },
            ],
            'Categories': [
                {
                    'Name': 'string'
                },
            ]
        },
        {
            'Name': 'string',
            'Confidence': '80',
            'Instances': []
        }

    ],
    'OrientationCorrection': 'ROTATE_0',
    'LabelModelVersion': 'string',
    'ImageProperties': {
        'Quality': {
            'Brightness': ...,
            'Sharpness': ...,
            'Contrast': ...
        },
        'DominantColors': [
            {
                'Red': 123,
                'Blue': 123,
                'Green': 123,
                'HexCode': 'string',
                'CSSColor': 'string',
                'SimplifiedColor': 'string',
                'PixelPercent': ...
            },
        ],
        'Foreground': {
            'Quality': {
                'Brightness': ...,
                'Sharpness': ...,
                'Contrast': ...
            },
            'DominantColors': [
                {
                    'Red': 123,
                    'Blue': 123,
                    'Green': 123,
                    'HexCode': 'string',
                    'CSSColor': 'string',
                    'SimplifiedColor': 'string',
                    'PixelPercent': ...
                },
            ]
        },
        'Background': {
            'Quality': {
                'Brightness': ...,
                'Sharpness': ...,
                'Contrast': ...
            },
            'DominantColors': [
                {
                    'Red': 123,
                    'Blue': 123,
                    'Green': 123,
                    'HexCode': 'string',
                    'CSSColor': 'string',
                    'SimplifiedColor': 'string',
                    'PixelPercent': ...
                },
            ]
        }
    }
}
#con = { "N": label["Confidence"] for label in response["Labels"]}
labels = {label["Name"]:{"N": label["Confidence"]} 
          for label in response["Labels"]}
print(labels)




item = {"file": "filename",
        "Labels": {"Label":"Confidence",
                  "Label":"Confidence",
                  "Label":"Confidence"}}

item = {"file": "filename",
        "label": "label",
        "Confidence": "Confidence"}