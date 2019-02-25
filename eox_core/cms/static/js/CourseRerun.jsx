import React from 'react';
import { TextArea, Button, StatusAlert, InputText } from '@edx/paragon'
import { LoadingIconComponent } from './LoadingIcon'
import { clientRequest } from './client'
import styles from '../css/CourseRerun'


export class CourseRerun extends React.Component {

  constructor(props) {
    super(props);

    this.organizationApiUrl = '/organizations';
    this.courseApiUrl = '/course';

    this.state = {
      courseKey: '',
      organizationList: '',
      organizationListTextArea: '',
      openAlert: false,
      completedTasks: [],
      failedTasks: [],
      statusAlertMessage: '',
      statusAlertType: '',
      isLoading: false
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
    this.handleOrganizationListChange = this.handleOrganizationListChange.bind(this);
  }

  componentDidMount() {
    this.getOrganizationList();
  }

  handleChange(value, name) {
    if (value !== name) {
      this.setState({
        [name]: value
      });
    }
  }

  getOrganizationList() {
    this.setState({
      isLoading: true
    });

    clientRequest(
      this.organizationApiUrl,
      'GET'
    )
    .then(
      res => this.handleResponse(res)
    )
    .then((response) => {
      this.fillOrganizationList(response);
    })
    .catch((error) => {
      this.openStatusAlert(`An error occurred while getting the organizations list: ${error.message}`, 'danger');
      this.setState({
        isLoading: false
      });
    });
  }

  handleSubmit() {
    const isValid = this.onSubmitValidator();
    let requestTimeOut = 0;

    if (isValid && confirm(`Rerun ${this.state.courseKey} course into ${this.state.organizationList.length} organizations.`)) {
      alert("enviando");
      // for (const org of this.state.organizationList) {
      //   setTimeout(() => {
      //     this.setState({
      //       isLoading: true
      //     });
      //     // const requetsBody = {
      //     //   source_course_key: this.state.courseKey,
      //     //   org: org,
      //     //   number:
      //     // }

      //     // clientRequest(
      //     //   courseApiUrl,
      //     //   'POST',
      //     //   requetsBody
      //     // )
      //     // .then(
      //     //   res => this.handlePostSettingsResponse(res, courseKey)
      //     // )
      //     // .catch((error) => {
      //     //   console.log(error.message);
      //     //   this.setState({
      //     //     isLoading: false
      //     //   });
      //     // });
      //   }, requestTimeOut);
      //   requestTimeOut += this.props.requestTimeOut
      // }
    }
  }

  onSubmitValidator() {
    const courseKey = this.state.courseKey;
    const organizationList = this.state.organizationList;

    if (courseKey === '') {
      this.openStatusAlert('Please, enter a valid course key.');
      return false;
    }

    if (organizationList.length === 0) {
      this.openStatusAlert('Please, enter a valid organization name/s.');
      return false;
    }

    return true;
  }

  courseKeyValidator() {
    const regex = /[^/+]+\+([^/+]+)\+([^/?+]+)/gm;
    const courseKey = this.state.courseKey;

    console.log(regex.exec(courseKey));
  }

  courseKeyExists() {
    const courseKey = this.state.courseKey;

    clientRequest(
      this.organizationApiUrl,
      'GET'
    )
    .then(
      res => this.handleResponse(res)
    )
    .then((response) => {
      this.fillOrganizationList(response);
    })
    .catch((error) => {
      this.openStatusAlert(`An error occurred while getting the organizations list: ${error.message}`, 'danger');
      this.setState({
        isLoading: false
      });
    });
  }

  fillOrganizationList(response) {
    const organizationList = response.join('\n');
    this.setState({
      organizationListTextArea: organizationList,
      organizationList: response,
      isLoading: false
    });
  }

  handleResponse(response) {
    if (response.ok)
      return response.json();

    throw new Error(response.statusText);
  }

  onCloseAlert() {
    this.setState({
      openAlert: false
    });
  }

  openStatusAlert(message, type) {
    this.setState({
      openAlert: true,
      statusAlertMessage: message,
      statusAlertType: type
    });
  }

  handleOrganizationListChange(value, name) {
    const organizationListRaw = value.split('\n');
    const organizationList = organizationListRaw.filter(value => {
      if (value !== '')
        return value;
    });
    this.setState({
      organizationList: organizationList
    });
  }

  render() {
    return (
    <div>
      <InputText
        name="courseKey"
        label="Course to rerun:"
        onChange={this.handleChange}
        value={this.state.courseKey}
      />
      <TextArea
        name="OrganizationList"
        className={[styles.organizationList]}
        label="Target organizations:"
        value={this.state.organizationListTextArea}
        onChange={this.handleOrganizationListChange}
      />
      <Button
        label="Rerun course."
        onClick={this.handleSubmit}
        className={['btn-primary btn-lg']}
      />
      <StatusAlert
        dialog={this.state.statusAlertMessage}
        onClose={this.onCloseAlert}
        open={this.state.openAlert}
        alertType={this.state.statusAlertType}
      />
      <div>
        <h2>Operations complete:</h2>
        <ol>{this.state.completedTasks}</ol>
        <h2>Operations not complete:</h2>
        <ol>{this.state.failedTasks}</ol>
      </div>
      {this.state.isLoading ? <LoadingIconComponent/> : null}
    </div>
    );
  }
}

