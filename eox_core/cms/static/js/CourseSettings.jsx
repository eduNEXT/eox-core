import React from 'react';
import { InputText, InputSelect, RadioButtonGroup, RadioButton, TextArea, Button, StatusAlert } from '@edx/paragon'
import { clientRequest } from './client'
import styles from '../css/CourseSettings.css'


export class CourseSettings extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      findCoursesRegex: '',
      openAlert: false,
      statusAlertMessage: '',
      statusAlertType: '',
      courseList: [],
      courseListHtml: [],
      advancedSettingList: [],
      detailsSettingList: [],
      hasAdvancedCourseSettings: false,
      settingTypeValue: '',
      detailsSettingValue: '',
      advancedSettingValue: '',
      advancedSettingName: '',
      detailsSettingName: ''
    }

    this.findCoursesRegexUrl = '/eox-core/management/get_courses';
    this.advancedSettingsUrl = '/settings/advanced/';
    this.detailSettingsUrl = '/settings/details/';

    this.handleChange = this.handleChange.bind(this);
    this.handleFindCoursesSubmit = this.handleFindCoursesSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
    this.onSubmitSetting = this.onSubmitSetting.bind(this);
    this.submitNewSetting = this.submitNewSetting.bind(this);
  }

  componentDidMount() {
    this.getCourseAdvancedSettings(this.props.courseKey);
    // Adds an empty value at the beginning of the details array.
    if (this.props.detailsFields.length !== 0) {
      const detailsSettingKeys = this.props.detailsFields;
      detailsSettingKeys.unshift('');
      this.setState({
        detailsSettingList: detailsSettingKeys
      });
    }
  }

  handleChange(value, name) {
    // We need to catch a TypeError error due to some Paragon components returns
    // as parameters the key pair value-name and other components returns
    // the generated event on its onChange event.
    // So, we need to capture both in order to update the state values.
    try {
      const elementValue = value.target.value;
      const elementName = value.target.name;
      this.setState({
        [elementName]: elementValue
      });
    } catch (error) {
      if (error instanceof TypeError) {
        if (value !== name) {
          this.setState({
            [name]: value
          });
        }
      } else {
        throw new Error(error);
      }
    }
  }

  handleFindCoursesSubmit() {

    if (this.state.findCoursesRegex === '') {
      this.setState({
        openAlert: true,
        statusAlertMessage: 'Please, enter a valid course regex.',
        statusAlertType: 'danger'
      });
      return;
    }

    this.setState({
      courseListHtml: [],
      openAlert: false
    });

    const searchStringScaped = this.state.findCoursesRegex.replace(/[+*]/gm, "%2B");
    const queryUrl = `${this.findCoursesRegexUrl}?search=${searchStringScaped}`;

    clientRequest(
      queryUrl,
      'GET'
    )
    .then(res => res.json())
    .then((response) => {
      if (response.status !== 'Failed')
        this.fillCourseList(response)
      else
        this.failedCourseRegexMatch(response)
    })
    .catch((error) => {
      console.log(error);
    });
  }

  onCloseAlert() {
    this.setState({
      openAlert: false
    });
  }

  fillCourseList(response) {
    let courseList = response.courses.map((courseKey) => {
      return <li key={courseKey}>{courseKey}</li>
    })

    this.setState({
      courseListHtml: courseList,
      courseList: response.courses
    });
  }

  failedCourseRegexMatch(response) {
    this.setState({
      openAlert: true,
      statusAlertMessage: response.message,
      statusAlertType: 'danger'
    });
  }

  getCourseAdvancedSettings(courseKey) {

    if (courseKey === '') {
      this.setState({
        hasAdvancedCourseSettings: false
      });
      return;
    }

    const queryUrl = `${this.advancedSettingsUrl}${this.props.courseKey}`
    clientRequest(
      queryUrl,
      'GET'
    )
    .then(res => res.json())
    .then((response) => {
      // Adds an empty value at the beginning of the settings array.
      const advancedSettingKeys = Object.keys(response);
      advancedSettingKeys.unshift('');
      this.setState({
        advancedSettingList: advancedSettingKeys
      });
    })
    .catch((error) => {
      console.log(error);
    });
  }

  onSubmitSetting() {
    this.setState({
      openAlert: false
    });

    const isValid = this.onSubmitValidator();
    if (isValid) {
      this.submitNewSetting();
    }
  }

  onSubmitValidator() {

    const settingTypeValue = this.state.settingTypeValue;

    if (this.state.courseList.length === 0) {
      this.setState({
        openAlert: true,
        statusAlertMessage: 'No courses selected to apply the changes.',
        statusAlertType: 'danger'
      });
      return false;
    }

    if (settingTypeValue === '') {
      this.setState({
        openAlert: true,
        statusAlertMessage: 'Please, select Schedule & details or Advanced settings.',
        statusAlertType: 'danger'
      });
      return false;
    }

    const typeSettingName = Object.getOwnPropertyDescriptor(this.state, `${settingTypeValue}SettingName`);
    const typeMessage = (settingTypeValue === 'details') ? 'Schedule & Details' : 'Advanced settings';

    if (typeSettingName.value === '') {
      this.setState({
        openAlert: true,
        statusAlertMessage: `Please enter a valid ${typeMessage} setting.`,
        statusAlertType: 'danger'
      });
      return false;
    }

    const fieldToCheck = Object.getOwnPropertyDescriptor(this.state, `${settingTypeValue}SettingValue`);
    if (fieldToCheck.value === '') {
      this.setState({
        openAlert: true,
        statusAlertMessage: `Please enter a valid ${typeMessage} value.`,
        statusAlertType: 'danger'
      });
      return false;
    }
    return true;
  }

  submitNewSetting() {
    const courses = this.state.courseList;
    const settingTypeValue = this.state.settingTypeValue;
    const typeSettingUrl = (settingTypeValue === 'details') ? this.detailSettingsUrl : this.advancedSettingsUrl;
    let requetsBody = {};

    if (settingTypeValue === 'details') {
      let settingName = this.state.detailsSettingName;
      let settingValue = this.state.detailsSettingValue;
      requetsBody = {
        [settingName]: this.convertToType(settingValue),
        intro_video: (settingName === 'intro_video') ? this.convertToType(settingValue) : null
      };
    }

    if (settingTypeValue === 'advanced') {
      let settingName = this.state.advancedSettingName;
      let settingValue = this.state.advancedSettingValue;
      requetsBody = {
        [settingName]: {
          value: this.convertToType(settingValue)
        }
      };
    }

    for (const courseKey of courses) {
      const queryUrl = `${typeSettingUrl}${courseKey}`;
      clientRequest(
        queryUrl,
        'POST',
        requetsBody
      )
      .then(res => res.json())
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });
    }
  }

  convertToType(value) {
    try {
      const typeValue = JSON.parse(value);

      if (typeof typeValue === 'boolean')
        return typeValue

      if (Array.isArray(typeValue))
        return typeValue

      if (typeof typeValue === 'object')
        return typeValue

      if (typeof typeValue === 'null')
        return null

    } catch (error) {
      if (error instanceof SyntaxError) {
        return value;
      } else {
        throw new Error(error);
      }
    }
    return value;
  }

  render() {
    return (
    <div>
      <div className="row">
        <div className="col-4">
          <InputText
            name="findCoursesRegex"
            label="Enter the course regex"
            onChange={this.handleChange}
            value={this.state.findCoursesRegex}
          />
          <Button
            label="Find courses"
            name="find"
            onClick={this.handleFindCoursesSubmit}
          ></Button>
        </div>
        <div className="col-8">
          <label>Current operation will apply to the following courses:</label>
          <div className={styles.coursesList}>
            <ul>{this.state.courseListHtml}</ul>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-4">
          <RadioButtonGroup
            name="settingTypeValue"
            label="Setting type"
            onChange={this.handleChange}
          >
            <RadioButton value="details">
              Schedule & Details
            </RadioButton>
            <RadioButton value="advanced">
              Advanced Settings
            </RadioButton>
          </RadioButtonGroup>
        </div>
        <div className="col-4">
          <InputSelect
            label="Schedule & Details"
            options={this.state.detailsSettingList}
            name="detailsSettingName"
            onChange={this.handleChange}
          />
        </div>
        <div className="col-4">
          <TextArea
            name="detailsSettingValue"
            label="New value"
            onChange={this.handleChange}
          />
        </div>
      </div>
      <div className="row">
        <div className="col-4">

        </div>
        <div className="col-4">
          <InputSelect
            label="Advanced Settings"
            options={this.state.advancedSettingList}
            name="advancedSettingName"
            onChange={this.handleChange}
          />
        </div>
        <div className="col-4">
          <TextArea
            name="advancedSettingValue"
            label="New value"
            onChange={this.handleChange}
          />
        </div>
      </div>
      <Button
        label="Apply changes"
        name="apply"
        onClick={this.onSubmitSetting}
      ></Button>
      <StatusAlert
        dialog={this.state.statusAlertMessage}
        onClose={this.onCloseAlert}
        open={this.state.openAlert}
        alertType={this.state.statusAlertType}
      />
    </div>
    );
  }
}